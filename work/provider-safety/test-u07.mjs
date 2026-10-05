import assert from "node:assert/strict";
import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import {
  APPROVED_INFISICAL_ORIGIN,
  PROJECT_ID,
  makeDefaultRunner,
  makeInfisicalKeyProvider,
} from "../jev-client/src/infisical-key.ts";

const SYNTHETIC = Object.freeze({
  clientId: "u07-synthetic-client-id",
  clientSecret: "u07-synthetic-client-secret",
  accessToken: "u07-synthetic-access-token",
  key: "u07-synthetic-typesafe-key",
  parentSentinel: "u07-parent-secret-sentinel",
});
const APPROVED_TEST_ORIGIN = APPROVED_INFISICAL_ORIGIN;
const LOGIN_PATH = "/api/v1/auth/universal-auth/login";
const CHILD_ARGS = ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"];
const PARENT_ENV = {
  PATH: "/synthetic/bin",
  HOME: "/synthetic/home",
  TMPDIR: "/synthetic/tmp",
  INFISICAL_CLIENT_SECRET: SYNTHETIC.parentSentinel,
  TYPESAFE_API_KEY: SYNTHETIC.parentSentinel,
  UNRELATED: SYNTHETIC.parentSentinel,
};

function config(apiUrl) {
  return [
    `export INFISICAL_CLIENT_ID=${SYNTHETIC.clientId}`,
    `export INFISICAL_CLIENT_SECRET=${SYNTHETIC.clientSecret}`,
    `export INFISICAL_API_URL=${apiUrl}`,
  ].join("\n");
}

function fakeExecFile(calls) {
  return (file, args, options, callback) => {
    calls.push({ file, args: [...args], env: { ...options.env } });
    if (calls.length === 1) callback(new Error("synthetic expired user session"), "", "");
    else callback(null, `${SYNTHETIC.key}\n`, "");
  };
}

function makeRunner(calls) {
  return makeDefaultRunner(fakeExecFile(calls), PARENT_ENV);
}

async function approvedOriginScenario() {
  const children = [];
  const requests = [];
  const runner = makeRunner(children);
  const transport = async (input, init) => {
    const url = new URL(String(input));
    const body = JSON.parse(init.body);
    requests.push({ url: url.href, init: { ...init, body }, body });
    return {
      ok: true,
      status: 200,
      redirected: false,
      url: url.href,
      json: async () => ({ accessToken: SYNTHETIC.accessToken }),
    };
  };
  const provider = makeInfisicalKeyProvider(
    runner,
    () => 0,
    "infisical",
    "/synthetic/home",
    () => config(`${APPROVED_TEST_ORIGIN}/api`),
    { origin: APPROVED_TEST_ORIGIN, transport },
  );

  assert.equal(await provider(), SYNTHETIC.key);
  assert.equal(requests.length, 1, "approved origin receives exactly one synthetic login request");
  assert.deepEqual(
    {
      url: requests[0].url,
      method: requests[0].init.method,
      redirect: requests[0].init.redirect,
      headers: requests[0].init.headers,
      body: requests[0].body,
    },
    {
      url: `${APPROVED_TEST_ORIGIN}${LOGIN_PATH}`,
      method: "POST",
      redirect: "error",
      headers: { "content-type": "application/json" },
      body: { clientId: SYNTHETIC.clientId, clientSecret: SYNTHETIC.clientSecret },
    },
  );
  assert.equal(children.length, 2, "one failed user-session lookup then one machine-key lookup");
  assert.deepEqual(children[0], {
    file: "infisical",
    args: CHILD_ARGS,
    env: { PATH: PARENT_ENV.PATH, HOME: PARENT_ENV.HOME, TMPDIR: PARENT_ENV.TMPDIR },
  });
  assert.deepEqual(children[1], {
    file: "infisical",
    args: CHILD_ARGS,
    env: {
      PATH: PARENT_ENV.PATH,
      HOME: PARENT_ENV.HOME,
      TMPDIR: PARENT_ENV.TMPDIR,
      INFISICAL_API_URL: APPROVED_TEST_ORIGIN,
      INFISICAL_TOKEN: SYNTHETIC.accessToken,
    },
  });
  assert.equal(JSON.stringify(children).includes(SYNTHETIC.clientSecret), false, "client secret never enters child argv/env");
  assert.equal(JSON.stringify(children).includes(SYNTHETIC.parentSentinel), false, "unrelated parent secrets are not inherited");
  assert.equal(children.some((child) => child.args.includes(SYNTHETIC.clientSecret)), false);

  return {
    returned_synthetic_key: true,
    external_network_calls: 0,
    synthetic_transport_calls: requests.length,
    request: {
      url: requests[0].url,
      method: requests[0].init.method,
      redirect: requests[0].init.redirect,
      header_names: Object.keys(requests[0].init.headers).sort(),
      body_fields: Object.keys(requests[0].body).sort(),
      client_id_matches_synthetic: requests[0].body.clientId === SYNTHETIC.clientId,
      client_secret_matches_synthetic: requests[0].body.clientSecret === SYNTHETIC.clientSecret,
    },
    children: children.map((child) => ({
      file: child.file,
      argv: child.args,
      env_names: Object.keys(child.env).sort(),
      parent_secret_inherited: Object.values(child.env).includes(SYNTHETIC.parentSentinel),
      client_secret_in_argv: child.args.includes(SYNTHETIC.clientSecret),
      machine_token_matches_synthetic: child.env.INFISICAL_TOKEN === SYNTHETIC.accessToken,
    })),
  };
}

async function deniedOriginScenario(apiUrl) {
  const children = [];
  let transportCalls = 0;
  const provider = makeInfisicalKeyProvider(
    makeRunner(children),
    () => 0,
    "infisical",
    "/synthetic/home",
    () => config(apiUrl),
    {
      origin: APPROVED_TEST_ORIGIN,
      transport: async () => {
        transportCalls++;
        throw new Error("denied origin must not reach transport");
      },
    },
  );

  assert.equal(await provider(), undefined);
  assert.equal(transportCalls, 0, `denied origin ${apiUrl} must not attempt a credential POST`);
  assert.equal(children.length, 1, "denied origin permits only the user-session lookup child");
  return { configured_origin: apiUrl, credential_post_attempts: transportCalls, child_invocations: children.length };
}

async function redirectScenario() {
  const children = [];
  const firstRecipient = `${APPROVED_TEST_ORIGIN}${LOGIN_PATH}`;
  const unapprovedRecipient = "https://collector.invalid/collect";
  const requestedUrls = [];
  const provider = makeInfisicalKeyProvider(
    makeRunner(children),
    () => 0,
    "infisical",
    "/synthetic/home",
    () => config(APPROVED_TEST_ORIGIN),
    {
      origin: APPROVED_TEST_ORIGIN,
      transport: async (input, init) => {
        const recipient = String(input);
        requestedUrls.push(recipient);
        assert.equal(recipient, firstRecipient, "unexpected recipient request is refused");
        assert.equal(init.redirect, "error", "the transport must be instructed not to follow redirects");
        // Simulate a transport that reports it followed an unexpected redirect.
        // No second synthetic request is made to the collector.
        return {
          ok: true,
          status: 200,
          redirected: true,
          url: unapprovedRecipient,
          json: async () => ({ accessToken: SYNTHETIC.accessToken }),
        };
      },
    },
  );

  assert.equal(await provider(), undefined, "redirected authentication response is refused");
  assert.deepEqual(requestedUrls, [firstRecipient], "redirect target receives no second request");
  assert.equal(children.length, 1, "refused redirect never starts the machine-key child");
  return {
    first_recipient: firstRecipient,
    redirect_policy: "error",
    reported_final_recipient: unapprovedRecipient,
    first_hop_calls: requestedUrls.filter((url) => url === firstRecipient).length,
    unapproved_second_request_calls: requestedUrls.filter((url) => url === unapprovedRecipient).length,
    credential_child_invocations: children.length - 1,
    refused: true,
  };
}

async function main() {
  if (process.argv.slice(2).join(" ") !== "--json") {
    throw new Error("usage: node work/provider-safety/test-u07.mjs --json");
  }

  const originalFetch = globalThis.fetch;
  let ambientFetchCalls = 0;
  globalThis.fetch = async () => {
    ambientFetchCalls++;
    throw new Error("ambient fetch forbidden in U07 synthetic proof");
  };

  try {
    const approved = await approvedOriginScenario();
    const denied = await Promise.all([
      deniedOriginScenario("https://collector.invalid"),
      deniedOriginScenario("http://secrets.zeststream.ai"),
    ]);
    const redirect = await redirectScenario();
    assert.equal(ambientFetchCalls, 0, "all requests use injected transports; no network fetch ran");

    const reviewer = process.env.JEV_REVIEWER ?? process.env.OMP_AGENT_NAME ?? process.env.USER ?? "unknown";
    const report = {
      bead: "jev-u07-infisical-argv-gi70",
      result: "PASS",
      run_at: new Date().toISOString(),
      reviewer_identity: {
        name: reviewer,
        pane: process.env.TMUX_PANE ?? null,
        source: process.env.JEV_REVIEWER ? "JEV_REVIEWER" : process.env.OMP_AGENT_NAME ? "OMP_AGENT_NAME" : "USER fallback",
        independent: false,
      },
      source: "work/jev-client/src/infisical-key.ts",
      network: { external_calls: 0, ambient_fetch_calls: ambientFetchCalls, injected_transport_calls: approved.synthetic_transport_calls + denied.reduce((sum, item) => sum + item.credential_post_attempts, 0) + redirect.first_hop_calls },
      approved_origin: approved,
      denied_origins: denied,
      redirect_refusal: redirect,
      no_real_credentials: true,
      no_live_infisical_or_typesafe_calls: true,
      no_independent_review_claim: true,
    };
    const serialized = `${JSON.stringify(report, null, 2)}\n`;
    for (const secret of Object.values(SYNTHETIC)) {
      assert.equal(serialized.includes(secret), false, "report must not emit even synthetic credential values");
    }
    await writeFile(fileURLToPath(new URL("./u07-receipt.json", import.meta.url)), serialized, "utf8");
    process.stdout.write(serialized);
  } finally {
    globalThis.fetch = originalFetch;
  }
}

main().catch((error) => {
  process.stderr.write(`${error.stack ?? error}\n`);
  process.exitCode = 1;
});
