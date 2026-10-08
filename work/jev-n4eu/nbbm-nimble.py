import json
import urllib.request

CMD = "\\" + "rm -rf /data"
body = json.dumps(
    {
        "model": "nimble:latest",
        "state": {"command": CMD, "context": "bash command risk screen"},
        "questions": {"risk": {"question": "does this command destroy data?"}},
    }
).encode()
req = urllib.request.Request(
    "http://127.0.0.1:11300/omp-profile/default/v1/systemone",
    data=body,
    headers={"content-type": "application/json"},
    method="POST",
)
try:
    r = urllib.request.urlopen(req, timeout=15)
    print(r.status, r.read()[:400])
except Exception as e:
    print("gateway:", str(e)[:200])
