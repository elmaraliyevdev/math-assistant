#!/usr/bin/env bash
# Create annotated git tags for Math Assistant v1.0 freeze.
# Run from repository root after all tests pass and changes are committed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: not a git repository. Initialize git and commit before tagging." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: working tree has uncommitted changes. Commit before tagging." >&2
  exit 1
fi

COMMIT="$(git rev-parse HEAD)"
echo "Tagging commit ${COMMIT}"

for tag in "runtime-core@1.8.0" "api@1.0.0" "web@1.0.0"; do
  if git rev-parse "$tag" >/dev/null 2>&1; then
    echo "Tag $tag already exists — skipping"
  else
    git tag -a "$tag" -m "Math Assistant v1.0 — $tag"
    echo "Created tag $tag"
  fi
done

echo ""
echo "Tags created. Push with:"
echo "  git push origin runtime-core@1.8.0 api@1.0.0 web@1.0.0"
