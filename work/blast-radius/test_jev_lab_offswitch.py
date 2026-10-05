import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURFACES = ("route", "review", "preaction", "observer")


class JevLabOffSwitchTests(unittest.TestCase):
    def run_node(self, script: str, home: Path) -> dict:
        env = os.environ.copy()
        env["HOME"] = str(home)
        completed = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            cwd=ROOT,
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            self.fail(
                f"node response was not JSON: {error}; stderr={completed.stderr!r}"
            )

    def run_node_targets(self, home: Path) -> None:
        env = os.environ.copy()
        env["HOME"] = str(home)
        targets = (
            (
                "work/omp-jev-route/test/route.test.mjs",
                "^(presence-OFF|an unset API key)",
            ),
            (
                "work/omp-jev-review/test/review.test.mjs",
                "^(presence-OFF|an unset API key|a real score is recorded)",
            ),
            (
                "work/omp-jev-preaction/test/preaction.test.mjs",
                "^(presence-OFF|fires on every pattern|ordinary daily commands)",
            ),
            (
                "work/omp-jev-observer/test/observer.test.mjs",
                "^(presence-OFF|success returns undefined|Jev error returns undefined)",
            ),
        )
        for path, pattern in targets:
            with self.subTest(path=path):
                completed = subprocess.run(
                    ["node", "--test", f"--test-name-pattern={pattern}", path],
                    cwd=ROOT,
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                self.assertIn("# fail 0", completed.stdout)

    def test_surface_handlers_keep_their_off_behaviors(self):
        with tempfile.TemporaryDirectory() as home:
            self.run_node_targets(Path(home))

    def test_all_surfaces_check_presence_on_each_call(self):
        script = r"""
          import { jevLabOff } from './work/jev-lab-offswitch.mjs';
          import { mkdir, readFile, writeFile } from 'node:fs/promises';
          import { join } from 'node:path';
          const root = join(process.env.HOME, '.local', 'state', 'jev');
          await mkdir(root, { recursive: true });
          const names = ['route', 'review', 'preaction', 'observer'];
          const results = {};
          for (const name of names) {
            const path = join(root, `jev-lab-${name}.off`);
            results[name] = [await jevLabOff(name)];
            await writeFile(path, 'operator off');
            results[name].push(await jevLabOff(name));
          }
          const log = (await readFile(join(root, 'jev-lab-calls.jsonl'), 'utf8')).trim().split('\n').map(JSON.parse);
          console.log(JSON.stringify({ results, log }));
        """
        with tempfile.TemporaryDirectory() as home:
            payload = self.run_node(script, Path(home))
        results = payload["results"]
        self.assertEqual(set(results), set(SURFACES))
        for values in results.values():
            self.assertEqual(values, [False, True])
        self.assertEqual(len(payload["log"]), 8)
        self.assertTrue(
            all(
                set(row) == {"timestamp", "surface", "status"} for row in payload["log"]
            )
        )
        for surface in SURFACES:
            self.assertEqual(
                [row["status"] for row in payload["log"] if row["surface"] == surface],
                ["on", "off"],
            )

    def test_switch_created_mid_session_is_seen_without_reload(self):
        script = r"""
          import { jevLabOff } from './work/jev-lab-offswitch.mjs';
          import { mkdir, writeFile } from 'node:fs/promises';
          import { join } from 'node:path';
          const root = join(process.env.HOME, '.local', 'state', 'jev');
          await mkdir(root, { recursive: true });
          const path = join(root, 'jev-lab-route.off');
          const first = await jevLabOff('route');
          await writeFile(path, 'operator off');
          const second = await jevLabOff('route');
          console.log(JSON.stringify([first, second]));
        """
        with tempfile.TemporaryDirectory() as home:
            result = self.run_node(script, Path(home))
        self.assertEqual(result, [False, True])

    def test_route_observes_a_marker_created_after_handler_start(self):
        script = r"""
          import assert from 'node:assert/strict';
          import { mkdir, writeFile } from 'node:fs/promises';
          import { join } from 'node:path';
          import route from './work/omp-jev-route/src/index.ts';
          const stateDir = join(process.env.HOME, '.local', 'state', 'jev');
          await mkdir(stateDir, { recursive: true });
          const marker = join(stateDir, 'jev-lab-route.off');
          let handler;
          const pi = { on: (_name, callback) => { handler = callback; }, appendEntry: async () => {} };
          let requests = 0;
          process.env.TYPESAFE_API_KEY = 'offline-test-key';
          globalThis.fetch = async () => {
            requests += 1;
            return new Response('unauthorized', { status: 401 });
          };
          route(pi);
          const event = { type: 'context', messages: [{ role: 'user', content: 'Refactor the auth boundary.' }] };
          await handler(event);
          const beforeMarker = requests;
          await writeFile(marker, 'operator off');
          await handler(event);
          assert.ok(beforeMarker > 0);
          assert.equal(requests, beforeMarker);
          console.log(JSON.stringify({ beforeMarker, afterMarker: requests }));
        """
        with tempfile.TemporaryDirectory() as home:
            result = self.run_node(script, Path(home))
        self.assertGreater(result["beforeMarker"], 0)
        self.assertEqual(result["afterMarker"], result["beforeMarker"])


if __name__ == "__main__":
    unittest.main()
