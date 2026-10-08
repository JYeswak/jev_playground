# `fm-hooks-global-link-broken`

`corrupt.sh` copies the tracked source hook to `TARGET`, preserving bytes but breaking inode identity. `assert.sh` succeeds only when `TARGET` is a hard link to `SOURCE`.
