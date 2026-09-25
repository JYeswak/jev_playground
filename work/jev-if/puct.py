"""MC-DML's PUCT search with a pluggable action prior (bead jev-jy7t.1.4).

Reference implementation: winni18/MC-DML @ 7f1312225c4a93cb7c3c6e93c4a6b9e0f739a0df
(`src/mcts.py`, `src/llm.py`, `src/env.py`, `main.py`). Line numbers below cite that commit.
This module reproduces the paper's Table 4 "w.o. Mc, Mi, DP" configuration:
no cross-trial reflections, fixed search depth, and one action prior per tree node.

Only the source of the prior changes between arms:
- `uniform`: 1/|A| over the valid actions.
- `jev`: one TypeSafe Choice over the valid actions (model pinned to jev-1.13.0).
Both arms go through `PriorService.get`, then the same MC-DML log-prob transform,
then `PUCTSearch.greedy_action_node`.

Stdlib only at import time; the TypeSafe SDK is imported lazily inside `SdkAsker`.
"""

import hashlib
import json
import math
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

MODEL = "jev-1.13.0"
BASE_URL = (
    "https://api.typesafe.ai"  # pinned: TYPESAFE_BASE_URL in the environment is ignored
)
DEATH_TEXT = "*** you have died ***"  # mcts.py:173
DEATH_REWARD = -10  # mcts.py:174
Q_SOFTMAX_T = 10  # mcts.py:202
PRIOR_SOFTMAX_T = 5  # main.py:38 (--softmax_temperature 5), llm.py:82
ABSENT_LOGPROB = -5  # llm.py:81 (the paper, Appendix B, says -10; the code uses -5)
MAX_CHOICE_OPTIONS = 255  # docs-mirror/typesafe/api.md, Choice `criteria`

# Per-game settings of the Table 4 "w.o. DP" ablation. MC-DML Appendix B: c_puct 50, 20 for
# Deephome, 200 for Detective, "following Jang et al. (2020)"; Section 4.3: without DP "we follow
# the experimental setup of Jang et al. (2020), using a fixed search depth for each game".
# Jang et al. (ICLR 2021) Appendix B Table 4: max search depth 10/10/10, max episode length 35/35/50.
GAMES = {
    "zork1": {"rom": "zork1.z5", "c_puct": 50, "max_depth": 10, "max_steps": 35},
    "deephome": {"rom": "deephome.z5", "c_puct": 20, "max_depth": 10, "max_steps": 35},
    "detective": {
        "rom": "detective.z5",
        "c_puct": 200,
        "max_depth": 10,
        "max_steps": 50,
    },
}

PROMPT = (
    "You are a player in a text-based adventure game. Your task is to evaluate and select actions "
    "that are promising based on the given game state. Considering the current state, please select "
    "the most promising action."
)  # llm.py:30 and llm.py:39, without the index-only answer format that a Choice makes redundant


class MissingKeyError(RuntimeError):
    """TYPESAFE_API_KEY is absent. Fatal: never converted into a uniform prior."""


class FatalPriorError(RuntimeError):
    """The key was rejected (HTTP 401/403). Fatal: never converted into a uniform prior."""


def softmax(values, temperature):
    """utils.py:3-8 with a max shift (same result, no overflow)."""
    scaled = [v / temperature for v in values]
    top = max(scaled)
    weights = [math.exp(v - top) for v in scaled]
    total = sum(weights)
    return [w / total for w in weights]


def softmax_backup(returns):
    """mcts.py:202: Q = sum(R * softmax(R, T=10)), not the plain mean of Algorithm 1 line 29."""
    return sum(r * w for r, w in zip(returns, softmax(returns, Q_SOFTMAX_T)))


def isclose(a, b):
    """numpy.isclose defaults (rtol 1e-5, atol 1e-8), used for tie detection at mcts.py:230."""
    if math.isinf(a) or math.isinf(b):
        return a == b
    return abs(a - b) <= 1e-8 + 1e-5 * abs(b)


def puct_value(q, n_parent, n_child, prior, c_puct):
    """mcts.py:228: Q + c * sqrt(N(s)+1) / (N(s,a)+1) * p."""
    return q + c_puct * math.sqrt(n_parent + 1) / (n_child + 1) * prior


def mcdml_transform(probabilities):
    """Map option probabilities to MC-DML's prior: softmax(max(log p, -5) / 5).

    MC-DML turns token log-probs into a prior with softmax at T=5 and gives labels absent from the
    top-20 a log-prob of -5 (llm.py:81-82). A Jev probability p is used as the token probability;
    p = 0, or any log p below -5, takes the absent-label value, which keeps the map monotone.
    """
    logits = [
        max(math.log(p), ABSENT_LOGPROB) if p > 0 else ABSENT_LOGPROB
        for p in probabilities
    ]
    return softmax(logits, PRIOR_SOFTMAX_T)


def raw_transform(probabilities):
    total = sum(probabilities)
    return [p / total for p in probabilities]


TRANSFORMS = {"mcdml": mcdml_transform, "raw": raw_transform}


def validate_choice(answer, options):
    """Refuse a malformed Choice answer; never coerce it (AGENTS.md, jev-ultrafast validate_choice)."""
    try:
        probabilities = answer["probabilities"]
        numbers = list(probabilities.values()) + [answer["confidence"]]
        valid = (
            answer["choice"] in options
            and set(probabilities) == set(options)
            and all(
                type(n) in (int, float) and math.isfinite(n) and 0 <= n <= 1
                for n in numbers
            )
            and abs(sum(probabilities.values()) - 1) <= 0.02
            and probabilities[answer["choice"]] >= max(probabilities.values()) - 1e-6
        )
    except (KeyError, TypeError, ValueError, AttributeError):
        valid = False
    if not valid:
        raise ValueError("Invalid Choice answer; node falls back to the uniform prior.")
    return answer


def unique(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


# ---------------------------------------------------------------------------------------------
# Tree (mcts.py:12-38, build_state mcts.py:63-88)


class StateNode:
    __slots__ = (
        "ob",
        "look",
        "inv",
        "state",
        "prev_state",
        "prev_action",
        "valid_actions",
        "history",
        "prior",
        "prior_future",
        "N",
        "children",
        "reward",
        "score",
        "done",
    )

    def __init__(self):
        self.prior = None
        self.prior_future = None
        self.N = 0
        self.children = []


class ActionNode:
    __slots__ = ("action", "N", "Q", "Rs", "children", "children_text")

    def __init__(self, action):
        self.action = action
        self.N = 0
        self.Q = 0
        self.Rs = []
        self.children = []
        self.children_text = {}  # first-match lookup, same as list.index at mcts.py:180


def build_state(
    ob, info, reward=0, done=False, prev_state="<s>", prev_action="<s>", history=()
):
    node = StateNode()
    node.ob = ob
    node.look = info["look"]
    node.inv = info["inv"]
    node.reward = reward
    node.score = info["score"]
    node.prev_action = prev_action
    node.prev_state = prev_state
    node.history = tuple(history)
    node.state = (
        ob + info["inv"] if ob == info["look"] else ob + info["look"] + info["inv"]
    )
    node.valid_actions = info["valid"]
    node.done = done
    node.children = [ActionNode(a) for a in info["valid"]]
    return node


def node_state(node, history_actions=3):
    """The Jev state: {observation, look, inventory, last actions, score} (WIZARD_IDEAS_CC.md:178)."""
    return {
        "observation": node.ob,
        "look": node.look,
        "inventory": node.inv,
        "last_actions": list(node.history[-history_actions:])
        if history_actions > 0
        else [],
        "score": node.score,
    }


# ---------------------------------------------------------------------------------------------
# Priors


def uniform_prior(state, actions):
    options = unique(actions)
    return {"probabilities": {a: 1.0 / len(options) for a in options}, "calls": 0}


class JevPrior:
    """One TypeSafe Choice per node; the options are the valid-action strings."""

    def __init__(self, asker, model=MODEL):
        self.asker = asker
        self.model = model

    def question(self, actions):
        return {
            "type": "choice",
            "instructions": PROMPT,
            "criteria": {a: None for a in unique(actions)},
        }

    def __call__(self, state, actions):
        options = unique(actions)
        if len(options) == 1:  # p = 1 whatever the answer; no call
            return {"probabilities": {options[0]: 1.0}, "calls": 0}
        if len(options) > MAX_CHOICE_OPTIONS:
            raise ValueError(
                "%d options exceed the Choice limit of %d"
                % (len(options), MAX_CHOICE_OPTIONS)
            )
        reply = self.asker(state, self.question(options), self.model)
        if reply.get("model") != self.model:
            raise ValueError(
                "resolved model %r is not the pinned %r"
                % (reply.get("model"), self.model)
            )
        validate_choice(reply["answer"], options)
        usage = reply.get("usage") or {}
        return {
            "probabilities": reply["answer"]["probabilities"],
            "calls": 1,
            "input_tokens": usage.get("input_tokens") or 0,
            "output_tokens": usage.get("output_tokens") or 0,
        }


class SdkAsker:
    """TypeSafe Choice through the official SDK (typesafe-sdk 0.7.1).

    Reads TYPESAFE_API_KEY at call time and raises MissingKeyError when it is absent; there is no
    local fallback. `transport` is an injectable httpx2 transport for offline tests.
    Retries are the SDK's RetryPolicy (408, 429, 5xx, connection errors, timeouts).
    """

    def __init__(self, transport=None, max_retries=2, timeout=20.0):
        self.transport = transport
        self.max_retries = max_retries
        self.timeout = timeout
        self._client = None
        self._key = None
        self._lock = threading.Lock()

    def _client_for(self, key):
        with self._lock:
            if self._client is None or key != self._key:
                from typesafe_sdk import RetryPolicy, TypeSafeClient

                self._client = TypeSafeClient(
                    api_key=key,
                    retry=RetryPolicy(max_retries=self.max_retries),
                    timeout=self.timeout,
                    transport=self.transport,
                    base_url=BASE_URL,
                )
                self._key = key
            return self._client

    def __call__(self, state, question, model):
        key = os.environ.get("TYPESAFE_API_KEY", "").strip()
        if not key:
            raise MissingKeyError(
                "TYPESAFE_API_KEY is not set; the jev arm refuses to run without it."
            )
        from typesafe_sdk import Choice, TypeSafeAPIError

        choice = Choice(
            instructions=question["instructions"], criteria=question["criteria"]
        )
        try:
            response = self._client_for(key).system_one(
                state=state, questions={"action": choice}, model=model
            )
        except TypeSafeAPIError as error:
            if error.status in (401, 403):
                raise FatalPriorError(
                    "TypeSafe rejected the key (HTTP %d)" % error.status
                ) from None
            raise
        answer = response.choices["action"]
        return {
            "model": response.model,
            "answer": {
                "choice": answer.choice,
                "confidence": answer.confidence,
                "probabilities": dict(answer.probabilities),
            },
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }


class FakeAsker:
    """Keyless stand-in: sleeps `latency` seconds, returns a seeded valid distribution. Dev only."""

    def __init__(self, latency=0.0, model=MODEL):
        self.latency = latency
        self.model = model

    def __call__(self, state, question, model):
        if self.latency:
            time.sleep(self.latency)
        options = list(question["criteria"])
        digest = hashlib.sha256(
            json.dumps([state, options], sort_keys=True).encode()
        ).digest()
        rng = random.Random(digest)
        weights = [rng.expovariate(1.0) for _ in options]
        total = sum(weights)
        probabilities = {o: w / total for o, w in zip(options, weights)}
        best = max(options, key=probabilities.get)
        return {
            "model": self.model,
            "answer": {
                "choice": best,
                "confidence": probabilities[best],
                "probabilities": probabilities,
            },
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }


class PriorService:
    """Owns every prior request, for both arms.

    Fail-safe: any error other than MissingKeyError/FatalPriorError (validator refusal, SDK error
    after its retries, timeout, >255 options, wrong model) gives that node the uniform prior and
    increments `failed`. The node is not asked again.
    `max_inflight > 1` runs requests on a thread pool; `prefetch(node)` starts a request early.
    The search always blocks on the node's own prior, so neither changes which prior a node gets.
    """

    def __init__(self, prior_fn, transform="mcdml", history_actions=3, max_inflight=1):
        self.prior_fn = prior_fn
        self.transform = TRANSFORMS[transform]
        self.history_actions = history_actions
        self.pool = ThreadPoolExecutor(max_inflight) if max_inflight > 1 else None
        self.lock = threading.Lock()
        self.requested = 0  # nodes that needed a prior (identical meaning in both arms)
        self.calls = 0  # network calls actually made
        self.failed = 0
        self.prefetched = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.wait_seconds = 0.0
        self.errors = []

    def _fetch(self, node):
        actions = node.valid_actions
        try:
            result = self.prior_fn(node_state(node, self.history_actions), actions)
        except (MissingKeyError, FatalPriorError):
            raise
        except Exception as error:  # fail-safe: uniform prior, counted
            with self.lock:
                self.failed += 1
                if len(self.errors) < 20:
                    self.errors.append("%s: %s" % (type(error).__name__, error))
            return {a: 1.0 / len(actions) for a in actions}
        with self.lock:
            self.calls += result.get("calls", 0)
            self.input_tokens += result.get("input_tokens", 0)
            self.output_tokens += result.get("output_tokens", 0)
        return result["probabilities"]

    def prefetch(self, node):
        if self.pool is None or node.prior is not None or node.prior_future is not None:
            return
        node.prior_future = self.pool.submit(self._fetch, node)
        with self.lock:
            self.prefetched += 1

    def get(self, node):
        if node.prior is not None:
            return node.prior
        started = time.monotonic()
        if node.prior_future is None:
            node.prior_future = (
                self.pool.submit(self._fetch, node) if self.pool else None
            )
        probabilities = (
            node.prior_future.result()
            if node.prior_future is not None
            else self._fetch(node)
        )
        self.wait_seconds += time.monotonic() - started
        self.requested += 1
        node.prior = self.transform(
            [probabilities[child.action] for child in node.children]
        )
        node.prior_future = None
        return node.prior

    def snapshot(self):
        with self.lock:
            return {
                "prior_requests": self.requested,
                "prior_calls": self.calls,
                "prior_failed": self.failed,
                "prior_prefetched": self.prefetched,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "prior_wait_s": round(self.wait_seconds, 3),
            }

    def close(self):
        if self.pool is not None:
            self.pool.shutdown(wait=True)


# ---------------------------------------------------------------------------------------------
# Search (mcts.py:91-277, Table 4 "w.o. Mc, Mi, DP")


class PUCTSearch:
    def __init__(
        self,
        env,
        priors,
        c_puct,
        rng,
        sims_per_act=50,
        discount=0.95,
        depth_schedule=(10, 10, 20),
        node_key="code",
        prefetch=False,
    ):
        self.env = env
        self.priors = priors
        self.c_puct = c_puct
        self.rng = rng
        self.sims_per_act = sims_per_act
        self.discount = discount
        self.d_min, self.d_max, self.d_step = depth_schedule
        self.node_key = node_key
        self.prefetch = prefetch
        self.env_steps = 0

    def search(self, ob, info, history=()):
        """mcts.py:91-113. With d_min == d_max the loop runs once: the "w.o. DP" fixed depth."""
        depth = self.d_min
        while depth <= self.d_max:
            root = build_state(ob, info, history=history)
            for _ in range(self.sims_per_act * len(root.children)):
                sim_env = self.env.copy()
                self.simulate(root, sim_env, 0, depth)
                sim_env.close()
            best = self.greedy_action_node(root, 0)
            if best.Rs and max(best.Rs) != 0:
                return root, best.action
            depth += self.d_step
        return root, best.action

    def _terminal(self, node, depth, max_depth):
        return (
            node.done
            or depth == max_depth
            or (node.look == "unknown" and node.inv == "unknown")
        )

    def _step(self, node, action_node, sim_env):
        prev_state = (
            node.ob + node.inv
            if node.ob == node.look
            else node.ob + node.look + node.inv
        )
        ob, reward, done, info = sim_env.step(action_node.action)
        self.env_steps += 1
        next_text = ob + info["look"] + info["inv"]
        if DEATH_TEXT in next_text:
            reward = DEATH_REWARD
        # mcts.py:179 looks children up by ob+look+inv but stores node.state (ob+inv when ob == look),
        # so a child whose ob equals its look is never found again. node_key="code" keeps that.
        key = next_text
        existing = action_node.children_text.get(key)
        created = existing is None
        if created:
            existing = build_state(
                ob,
                info,
                reward,
                done,
                prev_state,
                action_node.action,
                node.history + (action_node.action,),
            )
            action_node.children.append(existing)
            stored = existing.state if self.node_key == "code" else next_text
            action_node.children_text.setdefault(stored, existing)
        return existing, reward, created

    def simulate(self, node, sim_env, depth, max_depth):
        if self._terminal(node, depth, max_depth):
            return 0
        action_node = self.greedy_action_node(node, self.c_puct)
        child, reward, created = self._step(node, action_node, sim_env)
        rollout_next = created
        if not created:
            if child.N == 0:
                rollout_next = True
                if (
                    self.prefetch
                ):  # this child needs its prior on its next simulate visit
                    self.priors.prefetch(child)
            child.N += 1
        if rollout_next:
            R = reward + self.discount * self.rollout(
                child, sim_env, depth + 1, max_depth
            )
        else:
            R = reward + self.discount * self.simulate(
                child, sim_env, depth + 1, max_depth
            )
        node.N += 1
        action_node.N += 1
        action_node.Rs.append(R)
        action_node.Q = softmax_backup(action_node.Rs)
        return R

    def greedy_action_node(self, node, c_puct):
        probs = self.priors.get(node)
        best_value = -float("inf")
        best = []
        for child, p in zip(node.children, probs):
            value = puct_value(child.Q, node.N, child.N, p, c_puct)
            if isclose(value, best_value):
                best.append(child)
            elif value > best_value:
                best_value = value
                best = [child]
        return self.rng.choice(best)

    def rollout(self, node, sim_env, depth, max_depth):
        """mcts.py:241-277: uniform random valid action; nodes are added to the tree, no prior."""
        if self._terminal(node, depth, max_depth):
            return 0
        action_node = self.rng.choice(node.children)
        child, reward, _ = self._step(node, action_node, sim_env)
        return reward + self.discount * self.rollout(
            child, sim_env, depth + 1, max_depth
        )
