#!/usr/bin/env bash
# sync-docs.sh — vendor the PRIMARY sources this lane reads, locally and verifiably.
#   1. docs.typesafe.ai      → docs-mirror/typesafe/**.md   (via llms.txt, the doc site's own index)
#   2. github.com/typesafe-ai → upstream/typesafe-ai/<repo>  (first-party SDKs + agent skills)
#   3. ripwire               → docs-mirror/ripwire/*         (repo docs + the installed CLI's own help)
#   4. USAGE-MAP community sources → upstream/<owner>/<repo> (third-party Jev-ecosystem
#      repos at the EXACT cited SHA, detached — provenance for the demo backlog's numbers)
#
# Contract:
#   - IDEMPOTENT. Re-running overwrites mirrored bytes and rewrites the manifests. Nothing else.
#   - NEVER DESTRUCTIVE. No rm -rf, no git reset, no git clean, no checkout of an existing clone.
#     An existing clone is only ever `git fetch`ed; a SHA move is REPORTED, never performed.
#   - FAIL-CLOSED. An empty page set, a failed fetch, or a hash mismatch is an ERROR (nonzero),
#     never a silent pass. "Never fetched" must not read like "up to date".
#   - NO SECRETS. This script makes no authenticated API calls and never reads $TYPESAFE_API_KEY.
#
# Usage:
#   scripts/sync-docs.sh              # full sync (docs + repos + ripwire)
#   scripts/sync-docs.sh --check      # verify the mirror against MANIFEST.tsv; no network writes
#   scripts/sync-docs.sh --docs-only  # just docs.typesafe.ai
#   scripts/sync-docs.sh --repos-only # just the git surfaces
#
# Exit codes: 0 clean · 1 fetch/verify failure · 2 bad usage or missing tool · 3 empty scan set

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_HOST="https://docs.typesafe.ai"
ORG="typesafe-ai"
ORG_REPOS=(typesafe-sdk-python typesafe-sdk-js system-one-adapter-python skills)
RIPWIRE_URL="https://github.com/redhat-et/ripwire.git"
# COMMUNITY_REPOS: every third-party repo docs/demos/USAGE-MAP.md cites, as
# "owner/repo full-sha". Owners resolved 2026-09-18 via GitHub search + commit-SHA
# verification (receipt: bead jev-demo-loop-a1q.2); all 19 SHAs resolved, zero
# UNRESOLVABLE. Short SHAs in USAGE-MAP.md match these commits' prefixes.
COMMUNITY_REPOS=(
"jkudish/jev-mcp 6ec5efc6601477557c1436981ba69eb7b35832bd"
"NiazMorshed2007/jev-review 57690af54ef7d862c2483342c1e61c14dffcf727"
"browser-use/jev-ultrafast 452c1ad2dd628008f1d5608f28158d76e49e6cc0"
"gargpratyush/jev-router 86660a0248eba0e4523f81645ac2925e9808c000"
"0xNatoshi/jev-codex-router 8292b519659280884627a962c826ac7721136a64"
"anessbelbati/jev-rerank-bench cd9a35b22aeb4187334f7018a0ee1960a7470586"
"anisselbd/jev-phishing-bench 1d56e8c64d029a9554a0874e2ef2901ed196e230"
"Gaurav-Gosain/jev-sec-bench fdb16b94d37535db9bad77f8ef0faa971bd7d69a"
"bitnovus/jev-spam-eval 76ef18305710f8f38c984a56a80fc43e6bb18c6f"
"TokenTrim/jev-agent-failure-benchmark 4d46af795a4a4409940a65857da73e45abaea2db"
"iammrduncan/typesafe-ai-benchmark e94fcdaf5058da3e8988f525c3a647f53588d5f3"
"devanshbatham/commit-miner 977617ebce07c56b965253a68577b1d92b93fdf1"
"thruwire/foreman 2c439828b9fe45ee5d40f6f57be81f7ff1f8a140"
"AbdelStark/s1-rs b9168979a9beaeb74878483ff2876958acb98b86"
"Anil-matcha/awesome-jev-by-typesafe d57f5ce8002cc7cadc2c744b34a45933507e0508"
"AbdelStark/bicameral 3bea244b072cdacd3c8a85aec8d788a3ae0ac1cc"
"Dicklesworthstone/skillranker 3fe85c432ba5e2b4f980e842fc94d57fae6c4189"
"tamaratran/fast-jev-compaction 6e1da50d064cc06aa08e720b534b4d873e2bb0b6"
"typesafe-ai/system-one-adapter-python 0bb819b85d67a98c736d7c3004eae95f49f3daa3"
)
RIPWIRE_LOCAL="${RIPWIRE_LOCAL:-$HOME/Developer/ripwire}"
UA="OpenAI File Downloader, XaiImageApiFetch/1.0"

MIRROR="$ROOT/docs-mirror"
TS_DIR="$MIRROR/typesafe"
RW_DIR="$MIRROR/ripwire"
UP_DIR="$ROOT/upstream"
DOCS_MANIFEST="$MIRROR/MANIFEST.tsv"
REPO_MANIFEST="$UP_DIR/MANIFEST.tsv"
ORG_INVENTORY="$UP_DIR/ORG-INVENTORY.tsv"

MODE="all"
case "${1-}" in
  "")            MODE="all" ;;
  --check)       MODE="check" ;;
  --docs-only)   MODE="docs" ;;
  --repos-only)  MODE="repos" ;;
  -h|--help)     sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 0 ;;
  *)             echo "sync-docs: unknown argument '$1' (try --help)" >&2; exit 2 ;;
esac

need() { command -v "$1" >/dev/null 2>&1 || { echo "sync-docs: required tool missing: $1" >&2; exit 2; }; }
need curl; need git; need shasum; need sed; need grep; need sort

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
bytes() { wc -c <"$1" | tr -d ' '; }

fetch() { # fetch <url> <dest> ; atomic, retried, fail-closed
  local url="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if ! curl -fsSL --max-time 90 --retry 3 --retry-delay 2 -A "$UA" "$url" -o "$dest.part"; then
    echo "FAIL  fetch  $url" >&2
    rm -f -- "$dest.part" 2>/dev/null || true   # our own partial download, never a mirrored file
    return 1
  fi
  mv -f "$dest.part" "$dest"
}

# ---------------------------------------------------------------- check mode
if [ "$MODE" = check ]; then
  rc=0; n=0; bad=0
  [ -f "$DOCS_MANIFEST" ] || { echo "ERROR no docs manifest at $DOCS_MANIFEST — mirror was never built" >&2; exit 3; }
  while IFS=$'\t' read -r kind source local_path size digest fetched; do
    [ "$kind" = "kind" ] && continue
    n=$((n+1))
    local_abs="$ROOT/$local_path"
    if [ ! -f "$local_abs" ]; then echo "MISSING $local_path"; bad=$((bad+1)); continue; fi
    if [ "$(sha "$local_abs")" != "$digest" ]; then echo "DRIFT   $local_path"; bad=$((bad+1)); fi
  done < "$DOCS_MANIFEST"
  [ "$n" -eq 0 ] && { echo "ERROR manifest has zero rows — that is not a pass" >&2; exit 3; }
  if [ -f "$REPO_MANIFEST" ]; then
    while IFS=$'\t' read -r repo path pinned upstream_sha behind fetched; do
      [ "$repo" = "repo" ] && continue
      # `$HOME/...` is stored LITERALLY in upstream/MANIFEST.tsv, on purpose: a clone outside this
      # repo must be recorded portably, not pinned to one machine's absolute path. But the original
      # case had only `/*` and a repo-relative fallback, so `$HOME/Developer/ripwire` fell through to
      # `$ROOT/$HOME/Developer/ripwire` and the gate reported `MISSING clone` for a clone that EXISTS.
      # Measured 2026-09-18 (pane 3, 85d75a0 via Q84): CHECK FAIL 1 of 114, and `/Users/josh/
      # Developer/ripwire/.git` was present the whole time. A FALSE RED is the failure mode this lane
      # calls worse than a missed trip, because it teaches everyone to ignore the gate — so the fix
      # is to expand the portable prefixes, NOT to rewrite the manifest into a machine-specific path.
      case "$path" in
        /*)          abs="$path" ;;
        '$HOME'/*)   abs="$HOME/${path#\$HOME/}" ;;
        '${HOME}'/*) abs="$HOME/${path#\$\{HOME\}/}" ;;
        '~'/*)       abs="$HOME/${path#\~/}" ;;
        *)           abs="$ROOT/$path" ;;
      esac
      [ -d "$abs/.git" ] || { echo "MISSING clone $path"; bad=$((bad+1)); continue; }
      cur="$(git -C "$abs" rev-parse --short HEAD)"
      [ "$cur" = "$pinned" ] || echo "SHA-MOVED $path  manifest=$pinned head=$cur"
    done < "$REPO_MANIFEST"
  fi
  rcount=0
  [ -f "$REPO_MANIFEST" ] && rcount=$(($(wc -l < "$REPO_MANIFEST" | tr -d ' ') - 1))
  if [ "$bad" -gt 0 ]; then echo "CHECK FAIL  $bad of $n mirrored files missing or drifted ($rcount repo clones pinned)"; rc=1
  else echo "CHECK PASS  $n mirrored files match MANIFEST.tsv ($rcount repo clones pinned)"; fi
  exit $rc
fi

# ---------------------------------------------------------------- docs.typesafe.ai
sync_docs() {
  echo "== docs.typesafe.ai → docs-mirror/typesafe"
  mkdir -p "$TS_DIR"
  fetch "$DOCS_HOST/llms.txt"      "$TS_DIR/llms.txt"
  fetch "$DOCS_HOST/llms-full.txt" "$TS_DIR/llms-full.txt"
  fetch "$DOCS_HOST/sitemap.xml"   "$TS_DIR/sitemap.xml"

  # The doc site publishes its own machine-readable index. Trust it over a crawl.
  local pages; pages="$(grep -oE "$DOCS_HOST/[A-Za-z0-9._/-]+\.md" "$TS_DIR/llms.txt" | sort -u)"
  local count; count="$(printf '%s\n' "$pages" | grep -c . || true)"
  if [ "${count:-0}" -lt 1 ]; then
    echo "ERROR llms.txt yielded zero .md pages — empty scan set is a failure, not a pass" >&2
    exit 3
  fi
  echo "   llms.txt lists $count pages"

  local tmp_manifest; tmp_manifest="$(mktemp)"
  printf 'kind\tsource\tlocal_path\tbytes\tsha256\tfetched_at\n' > "$tmp_manifest"
  for f in llms.txt llms-full.txt sitemap.xml; do
    printf 'index\t%s\t%s\t%s\t%s\t%s\n' "$DOCS_HOST/$f" "docs-mirror/typesafe/$f" \
      "$(bytes "$TS_DIR/$f")" "$(sha "$TS_DIR/$f")" "$(now)" >> "$tmp_manifest"
  done

  local ok=0 fail=0
  while IFS= read -r url; do
    [ -n "$url" ] || continue
    local rel dest; rel="${url#"$DOCS_HOST"/}"; dest="$TS_DIR/$rel"
    if fetch "$url" "$dest"; then
      ok=$((ok+1))
      printf 'page\t%s\t%s\t%s\t%s\t%s\n' "$url" "docs-mirror/typesafe/$rel" \
        "$(bytes "$dest")" "$(sha "$dest")" "$(now)" >> "$tmp_manifest"
    else
      fail=$((fail+1))
    fi
  done <<< "$pages"

  mv -f "$tmp_manifest" "$DOCS_MANIFEST"
  echo "   pages ok=$ok fail=$fail  →  $DOCS_MANIFEST"
  [ "$fail" -eq 0 ] || { echo "ERROR $fail page(s) failed; mirror is incomplete" >&2; return 1; }
}

# ---------------------------------------------------------------- git surfaces
record_repo() { # record_repo <name> <path>   ; path may be workspace-relative or absolute
  local name="$1" path="$2" abs rec
  case "$path" in /*) abs="$path" ;; *) abs="$ROOT/$path" ;; esac
  # The manifest is a PUBLISHED artifact, so it must carry no operator home directory, and a
  # consumer must be able to re-derive the location. Record repo-relative when the clone is
  # inside this repo; otherwise substitute the literal string $HOME so the row stays portable.
  case "$abs" in
    "$ROOT"/*) rec="${abs#"$ROOT"/}" ;;
    "$HOME"/*) rec="\$HOME/${abs#"$HOME"/}" ;;
    *)         rec="$abs" ;;
  esac
  local pinned upstream_sha behind
  pinned="$(git -C "$abs" rev-parse --short HEAD)"
  upstream_sha="$(git -C "$abs" rev-parse --short FETCH_HEAD 2>/dev/null || echo "$pinned")"
  behind="$(git -C "$abs" rev-list --count "HEAD..FETCH_HEAD" 2>/dev/null || echo 0)"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$rec" "$pinned" "$upstream_sha" "$behind" "$(now)" >> "$REPO_MANIFEST"
  if [ "${behind:-0}" -gt 0 ]; then
    echo "   $name @ $pinned  ** $behind commit(s) behind $upstream_sha — SHA move is a human decision, not this script's **"
  else
    echo "   $name @ $pinned  (current)"
  fi
}

sync_community() {
  echo "== USAGE-MAP community sources → upstream/<owner>/<repo> @ cited SHA (detached)"
  for spec in "${COMMUNITY_REPOS[@]}"; do
    local owner_repo="${spec% *}" full="${spec#* }"
    local owner="${owner_repo%/*}" repo="${owner_repo#*/}"
    local path="upstream/$owner/$repo"
    local abs="$ROOT/$path"
    if [ -d "$abs/.git" ]; then
      git -C "$abs" fetch --quiet origin "$full" 2>/dev/null \
        || echo "   warn: fetch failed for $owner_repo (offline?)"
    else
      echo "   cloning $owner_repo"
      mkdir -p "$ROOT/upstream/$owner"
      git clone --quiet "https://github.com/$owner/$repo.git" "$abs" \
        || { echo "FAIL  clone $owner_repo" >&2; return 1; }
      [ -d "$abs/.git" ] || { echo "FAIL  clone reported success but $path has no .git" >&2; return 1; }
      git -C "$abs" fetch --quiet origin "$full" 2>/dev/null || true
    fi
      if ! git -C "$abs" checkout --quiet "$full" 2>/dev/null; then
        # Cited SHA not fetchable (dangling after upstream rewrite, or pruned).
        # Recorded, not silent: item 5 marks these UNRESOLVABLE in USAGE-MAP.md
        # itself; the pin set stays check-clean without them.
        grep -q "^${owner_repo}	" "$UP_DIR/UNRESOLVABLE.tsv" 2>/dev/null \
          || printf '%s\t%s\t%s\n' "$owner_repo" "$full" "$(now)" >> "$UP_DIR/UNRESOLVABLE.tsv"
        echo "   UNRESOLVABLE $owner_repo @ ${full:0:7} (cited SHA not fetchable upstream)"
        continue
      fi
    record_repo "$repo" "$path"
  done
}

sync_repos() {
  echo "== github.com/$ORG → upstream/$ORG"
  mkdir -p "$UP_DIR/$ORG"
  printf 'repo\tpath\tpinned_sha\tupstream_sha\tbehind\tfetched_at\n' > "$REPO_MANIFEST"

  for r in "${ORG_REPOS[@]}"; do
    local path="upstream/$ORG/$r"
    local abs="$ROOT/upstream/$ORG/$r"
    if [ -d "$abs/.git" ]; then
      git -C "$abs" fetch --quiet origin 2>/dev/null || echo "   warn: fetch failed for $r (offline?)"
    else
      echo "   cloning $r"
      git clone --quiet --depth 50 "https://github.com/$ORG/$r.git" "$abs"
      git -C "$abs" fetch --quiet origin 2>/dev/null || true
    fi
    record_repo "$r" "$path"
  done

  sync_community

  # ripwire: reuse the existing local checkout when present; never clone twice.
  local rw_path rw_abs
  if [ -d "$RIPWIRE_LOCAL/.git" ]; then
    rw_abs="$RIPWIRE_LOCAL"; rw_path="$RIPWIRE_LOCAL"
    git -C "$rw_abs" fetch --quiet origin 2>/dev/null || echo "   warn: fetch failed for ripwire (offline?)"
    echo "   ripwire: using existing checkout at $RIPWIRE_LOCAL"
  else
    rw_abs="$ROOT/upstream/ripwire"; rw_path="upstream/ripwire"
    [ -d "$rw_abs/.git" ] || { echo "   cloning ripwire"; git clone --quiet --depth 50 "$RIPWIRE_URL" "$rw_abs"; }
    git -C "$rw_abs" fetch --quiet origin 2>/dev/null || true
  fi
  record_repo ripwire "$rw_path"   # provenance is not optional for the checkout we actually read

  # Full org inventory, so nothing in the org is silently outside the allow-list above.
  if command -v gh >/dev/null 2>&1; then
    printf 'repo\tis_fork\tpushed_at\tmirrored\tdescription\n' > "$ORG_INVENTORY"
    gh repo list "$ORG" --limit 100 --json name,isFork,pushedAt,description 2>/dev/null \
      | jq -r --arg allow "${ORG_REPOS[*]}" '
          ($allow | split(" ")) as $a
          | .[] | [.name, (.isFork|tostring), .pushedAt,
                   (if (.name|IN($a[])) then "yes" else "no" end),
                   ((.description // "-") | gsub("\t"; " "))] | @tsv' >> "$ORG_INVENTORY" \
      || echo "   warn: org inventory unavailable"
    echo "   org inventory → $ORG_INVENTORY"
  fi

  # ripwire's docs + the installed binary's own help are the ripwire reading surface.
  mkdir -p "$RW_DIR"
  local src="$rw_abs"
  for f in README.md CHANGELOG.md AGENTS.md; do
    [ -f "$src/$f" ] && cp -f "$src/$f" "$RW_DIR/$f"
  done
  if [ -d "$src/docs" ]; then
    mkdir -p "$RW_DIR/docs"
    find "$src/docs" -maxdepth 1 -name '*.md' -exec cp -f {} "$RW_DIR/docs/" \;
  fi
  if command -v ripwire >/dev/null 2>&1; then
    ripwire --version  > "$RW_DIR/VERSION.txt"      2>&1 || true
    ripwire --help     > "$RW_DIR/CLI-HELP.txt"     2>&1 || true
    # 0.6.1 split the manual: --help is the ~200-line summary, --help=all is every flag in full.
    ripwire --help=all > "$RW_DIR/CLI-HELP-ALL.txt" 2>&1 || true
    echo "   ripwire docs → $RW_DIR  ($(head -1 "$RW_DIR/VERSION.txt" 2>/dev/null))"
    echo "   ripwire help → $(wc -l <"$RW_DIR/CLI-HELP.txt" | tr -d ' ') lines summary, $(wc -l <"$RW_DIR/CLI-HELP-ALL.txt" | tr -d ' ') lines full"
  else
    echo "   warn: ripwire not on PATH — CLI help not captured"
  fi
}

case "$MODE" in
  all)   sync_docs; sync_repos ;;
  docs)  sync_docs ;;
  repos) sync_repos ;;
esac

echo
echo "SYNC DONE  $(now)"
echo "  docs   : $TS_DIR            ($(find "$TS_DIR" -name '*.md' 2>/dev/null | wc -l | tr -d ' ') markdown pages)"
echo "  ripwire: $RW_DIR"
echo "  repos  : $REPO_MANIFEST"
echo "  verify : scripts/sync-docs.sh --check"
