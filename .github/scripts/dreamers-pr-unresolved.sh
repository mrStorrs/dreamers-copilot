#!/usr/bin/env bash
# Get unresolved review threads for a PR via GraphQL.
# REST `resolved` field is unreliable — always use GraphQL.
# Usage: get-unresolved-pr-comments.sh <PR_NUMBER> [REPO]
#   REPO defaults to the current repo (owner/name).
# Output: JSON array of {threadId, path, body} for isResolved=false threads.
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <PR_NUMBER> [owner/repo]" >&2
  exit 2
fi

pr="$1"
repo="${2:-}"
if [ -z "$repo" ]; then
  repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
fi
owner="${repo%%/*}"
name="${repo##*/}"

gh api graphql \
  -f query='query($owner:String!,$name:String!,$pr:Int!){repository(owner:$owner,name:$name){pullRequest(number:$pr){reviewThreads(first:100){nodes{id isResolved comments(first:1){nodes{path body}}}}}}}' \
  -F owner="$owner" -F name="$name" -F pr="$pr" \
  --jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false) | {threadId: .id, path: .comments.nodes[0].path, body: .comments.nodes[0].body}]'
