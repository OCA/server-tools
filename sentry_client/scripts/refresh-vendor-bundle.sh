#!/usr/bin/env bash
# Copyright 2026 Ledoent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# refresh-vendor-bundle.sh — pull the Sentry browser SDK UMD bundles down from
# browser.sentry-cdn.com, verify them against Sentry's published SRI hashes,
# and stage them under static/lib/sentry/<version>/ so the runtime never needs
# to reach a public CDN.
#
# Usage: ./refresh-vendor-bundle.sh [VERSION]
#   VERSION defaults to PINNED_VERSION below. Example: ./refresh-vendor-bundle.sh 10.55.0
#
# Run from the module root (sentry_client/), then `git add static/lib/sentry/<v>/`
# and commit.

set -euo pipefail

PINNED_VERSION="10.53.1"
VERSION="${1:-$PINNED_VERSION}"

CDN="https://browser.sentry-cdn.com"
REGISTRY="https://release-registry.services.sentry.io/sdks/sentry.javascript.browser/${VERSION}"

OUT_DIR="$(cd "$(dirname "$0")/.." && pwd)/static/lib/sentry/${VERSION}"
mkdir -p "${OUT_DIR}"

# Bundles to vendor — keep in sync with controllers/main.py::_bundle_name().
# Each name produces both `.min.js` + `.min.js.map`. Profiling is included in
# every bundle as of Sentry SDK 10.x — no separate profiling bundle file.
BUNDLES=(
  "bundle.min.js"
  "bundle.tracing.min.js"
  "bundle.tracing.replay.min.js"
  "bundle.feedback.min.js"
  "bundle.tracing.replay.feedback.min.js"
  # Add-on bundle for browser CPU profiling. Loaded as a second <script>
  # AFTER the main bundle by sentry_loader.js when the Tier 3 profiling
  # toggle is on. Augments window.Sentry with browserProfilingIntegration.
  "browserprofiling.min.js"
)

# Fetch Sentry's release manifest once for SRI hashes.
echo "==> Fetching release manifest for SDK ${VERSION}"
MANIFEST="$(curl -fsS "${REGISTRY}")"
if [ -z "${MANIFEST}" ]; then
  echo "ERROR: could not load release manifest at ${REGISTRY}" >&2
  exit 1
fi

# Verify a single file's bytes against its SRI sha384 hash via python.
verify_sri() {
  local path="$1"
  local expected_sha384="$2"
  python3 - "$path" "$expected_sha384" <<'PY'
import base64, hashlib, sys
path, expected = sys.argv[1], sys.argv[2]
with open(path, "rb") as f:
    h = hashlib.sha384(f.read()).digest()
actual = base64.b64encode(h).decode()
if actual != expected:
    print(f"SRI MISMATCH for {path}", file=sys.stderr)
    print(f"  expected sha384-base64: {expected}", file=sys.stderr)
    print(f"  actual:                 {actual}", file=sys.stderr)
    sys.exit(1)
print(f"  ok  sha384-base64={actual[:24]}…  {path.rsplit('/',1)[-1]}")
PY
}

extract_sha384() {
  local filename="$1"
  python3 - "$filename" <<PY
import json, sys
m = json.loads('''${MANIFEST}''')
fn = sys.argv[1]
files = m.get("files", {})
if fn not in files:
    print("", end="")
else:
    print(files[fn]["checksums"]["sha384-base64"], end="")
PY
}

echo "==> Downloading + verifying bundles into ${OUT_DIR}"
for bundle in "${BUNDLES[@]}"; do
  for variant in "${bundle}" "${bundle}.map"; do
    url="${CDN}/${VERSION}/${variant}"
    out="${OUT_DIR}/${variant}"
    echo "    -> ${variant}"
    curl -fsS "${url}" -o "${out}"
    expected="$(extract_sha384 "${variant}")"
    if [ -n "${expected}" ]; then
      verify_sri "${out}" "${expected}"
    else
      echo "    (no SRI hash for ${variant} in release manifest — skipping verify)"
    fi
  done
done

# Generate a SHA256SUMS file so reviewers can re-verify the committed blobs
# offline. Note: the SHA-384 checks above are against Sentry's published
# release manifest (proves "this matches what Sentry shipped"); SHA256SUMS
# is just for "the bytes haven't drifted since this commit" — different
# threat models, both useful.
echo "==> Writing SHA256SUMS"
(cd "${OUT_DIR}" && shasum -a 256 ./*.js ./*.js.map | sed 's| \./| |g' > SHA256SUMS)

# Drop the upstream LICENSE next to the bundles.
cat > "${OUT_DIR}/LICENSE" <<'LICENSE_END'
The Sentry JavaScript browser SDK is licensed under the MIT License.

MIT License

Copyright (c) 2019 Sentry (https://sentry.io) and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Upstream: https://github.com/getsentry/sentry-javascript
LICENSE_END

echo
echo "==> Done. Staged under: ${OUT_DIR}"
echo "    git add static/lib/sentry/${VERSION} && git commit"
