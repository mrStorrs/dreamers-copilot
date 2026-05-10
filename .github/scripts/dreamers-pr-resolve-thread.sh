#!/usr/bin/env bash
# Resolve a single PR review thread by its GraphQL node ID.
# Usage: resolve-pr-thread.sh <THREAD_ID>
# Output: "<threadId>\tresolved" on success, exits non-zero on failure.
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <THREAD_ID>" >&2
  exit 2
fi

thread_id="$1"

result=$(gh api graphql \
  -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' \
  -F id="$thread_id" \
  --jq '.data.resolveReviewThread.thread.isResolved')

if [ "$result" = "true" ]; then
  printf '%s\tresolved\n' "$thread_id"
else
  printf '%s\tFAILED\n' "$thread_id" >&2
  exit 1
fi
