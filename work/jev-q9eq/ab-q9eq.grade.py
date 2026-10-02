import json, subprocess

man = [json.loads(l) for l in open("var/agent-tmp/ab-q9eq.main/manifest.jsonl")]
GRADE = {
    "hard": "work/thinking-duel-hard/grade.py",
    "hard3": "work/thinking-duel-hard3/grade.py",
}
for r in man:
    d = "var/agent-tmp/ab-q9eq.main/%s-%s-%s" % (r["task"], r["arm"], r["rep"])
    p = subprocess.run(
        ["python3", GRADE[r["set"]], r["task"], d],
        capture_output=True,
        text=True,
        timeout=150,
        cwd="/Users/josh/Developer/jev",
    )
    print(r["task"], r["arm"], r["rep"], p.stdout.strip()[:60])
