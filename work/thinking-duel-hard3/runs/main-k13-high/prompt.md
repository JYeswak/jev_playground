# Task k13: chunked base64 decoder

Work in $PWD. `b64x.py` has `decode_chunks(chunks)` decoding base64 text
arriving in ARBITRARY chunks (chunk boundaries may split anywhere, even
inside `%`-escapes... no escapes: raw base64 alphabet plus whitespace which
must be ignored). Padding `=` only valid at the very end; `=` elsewhere or
missing terminal padding raises ValueError; non-alphabet chars (besides
whitespace) raise ValueError. shipped code joins-then-decodes without
validating padding placement. Fix it, stdlib `base64` allowed. Verify with
odd splits yourself.
