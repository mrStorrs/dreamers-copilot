---
name: dreamers-issue
description: 'Verify a task against the code, resolve concerns, and propose a minimal GitHub issue for approval before creating it. Triggers: /dreamers-issue, create an issue, open a GitHub issue, file an issue.'
argument-hint: '<task description>'
---

Evaluate the following request and propose a GitHub issue:

$ARGUMENTS

## User overrides

- Explicit user instructions can skip or alter phases/actions.

Follow YAGNI principles throughout: solve the demonstrated need with the smallest useful scope. Prefer existing capabilities and conventions; do not add speculative features, abstractions, or unrelated cleanup.

## Step 1: Take in the task

- Identify the intended outcome, reported problem, and constraints. If no task is provided, ask for it and wait.
- Run `gh repo view --json nameWithOwner` to confirm the target repository. If the repository cannot be determined, ask the user for the target (`OWNER/REPO`) and access to its code before continuing.
- Read the project's instructions. A leading `#` is accepted for compatibility; strip it and use this same workflow for every request.

## Step 2: Verify against the code

- Inspect the relevant implementation, callers, configuration, and tests as needed to establish current behaviour and check the request's assumptions. Follow the affected path far enough to support the findings; do not impose an arbitrary lookup limit or perform a repo-wide audit.
- Cite relevant file paths and symbols when summarizing what exists, what is missing, and whether existing behaviour already meets the need. Distinguish code evidence from unverified assumptions; do not claim runtime verification unless performed.
- If the relevant code is unavailable or evidence is insufficient, explain the gap, ask for what is needed, and wait before proposing a solution.
- This is investigation only: do not implement changes or create an issue during verification.

## Step 3: Resolve questions and concerns

- Present the verified findings before proposing a solution. Challenge incorrect assumptions, unnecessary scope, and conflicts with existing behaviour; explain the concern and recommend a simpler alternative where appropriate.
- Ask focused questions only for unresolved decisions affecting the outcome, scope, or acceptance criteria. Help the user reach a concrete solution and wait for answers before drafting the proposal.
- If the task is already clear, state that no questions remain and proceed. If the need is already met, explain how to use the existing capability and confirm whether any issue is still needed rather than inventing work.
- Recheck affected code when answers change the scope or invalidate earlier findings.

## Step 4: Present the proposal

- Run `gh label list` for the target repository and select appropriate existing labels only; omit labels if none fit.
- Use `~/.copilot/dreamers/templates/github-issue.md` to draft a concise title and complete issue body, grounded in the verified findings and resolved discussion. Show the title, body, and labels to the user.
- Keep scope minimal and explicit. Write concrete, testable acceptance criteria from a product owner perspective: observable outcomes rather than implementation instructions. Do not use speculative `[potential]` criteria.
- Ask for approval of this proposal and wait. Discussion or approval to investigate is not approval to create the issue. If revisions are requested, revisit verification and questions as needed, then present the revised proposal for approval.

## Step 5: Create the approved issue

- Only after approval of the current proposal, run `gh issue create` for the confirmed repository with the approved title, body, and existing label(s). Use a body file for multiline content.
- If creation fails, report the failure without claiming an issue exists. If the result is uncertain, check for an existing issue before retrying to avoid duplicates.
- Report the issue URL when creation succeeds.
