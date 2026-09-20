#!/bin/bash
# repro-4 — the ledger's state_preview stores raw state; the redactor masks PII but not
#           credentials, and the file is world-readable with no opt-out.
#
# PREREQUISITES: jevcache on PATH (curl -fsSL jevcache.sh/install | sh), python3.
#                NO API key, NO network, NO access to any repo. Throwaway HOME; your real
#                ~/.jevcache is never touched. Every secret below is fake.
set -u

W=$(mktemp -d); cd "$W"
export HOME="$W/home"; mkdir -p "$HOME"
cat > jevcache.schemas.json <<'EOF'
[{"id":"probe","version":1,"questions":{"q":{"instructions":"Is this destructive?","type":"noul"}}}]
EOF
export JEVCACHE_BACKEND=mock
echo "jevcache $(jevcache version)   HOME=$HOME   backend=mock"
echo

show_last_preview () {
  python3 - "$HOME/.jevcache/ledger.log" <<'PY'
import sys, json
last = None
for line in open(sys.argv[1]):
    o = json.loads(line)
    if o.get("t") == "put": last = o["r"]["state_preview"]
print(last)
PY
}

probe () {
  printf '%s' "$2" > "st$1.json"
  jevcache decide --schema probe --state "st$1.json" --json >/dev/null
  printf '  %-12s in  : %s\n' "$1" "$2"
  printf '  %-12s out : %s\n' "" "$(show_last_preview)"
}

echo "=== field by field: what reaches the on-disk state_preview ==="
probe email    '{"email":"alice.roberts@example.com"}'
probe phone    '{"phone":"+1 415 555 0199"}'
probe card     '{"card":"4111 1111 1111 1111"}'
probe ssn      '{"ssn":"123-45-6789"}'
probe password '{"password":"hunter2-correct-horse-battery"}'
probe apikey   '{"api_key":"sk-live-FAKE-EXAMPLE-NOT-A-REAL-KEY"}'
probe bearer   '{"authorization":"Bearer FAKE-EXAMPLE-NOT-A-REAL-TOKEN"}'
probe secret   '{"secret":"s3cr3t-value-not-a-number"}'
probe privkey  '{"private_key":"-----BEGIN RSA PRIVATE KEY-----FAKE-----END RSA PRIVATE KEY-----"}'
probe awskey   '{"aws":"AKIAIOSFODNN7EXAMPLE"}'
probe aws_id   '{"aws_access_key_id":"AKIAIOSFODNN7EXAMPLE"}'
probe hdr      '{"headers":{"Authorization":"Bearer FAKE-TOKEN-0000000000000000"}}'

echo
echo "=== and the file they all land in ==="
ls -l "$HOME/.jevcache/ledger.log"
echo
echo "PII rules fire (email/phone/digit-runs masked; *_id and timestamps dropped)."
echo "Credentials are not a category: password, api_key, Authorization: Bearer, secret and"
echo "private_key are written verbatim, into a mode-0644 file, with no flag to turn the"
echo "preview off."
exit 0
