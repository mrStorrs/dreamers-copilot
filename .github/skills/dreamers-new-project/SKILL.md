---
name: dreamers-new-project
description: 'Bootstrap a brand new project from scratch: discovery questions, project brief, shell plans. Triggers: /dreamers-new-project, new project, bootstrap a project, start a new project.'
argument-hint: '(no args; discovery is conversational)'
---

Bootstrap a brand new project from scratch. Work through the phases in order. Do not skip ahead or write anything permanent until the user explicitly approves the brief.

Read these refs:
- `~/.copilot/dreamers/refs/project-bootstrap.md`
- `~/.copilot/dreamers/refs/plan-rules.md`

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

$ARGUMENTS

---

## Todo list

At skill entry, declare via `manage_todo_list`:
- [ ] Phase 1 — discovery questions
- [ ] Phase 2 — tech stack recommendation + iteration
- [ ] Phase 3 — project brief + approval
- [ ] Phase 4 — repo & workspace bootstrap
- [ ] Phase 5 — shell plans
- [ ] Phase 6 — review loop

Mark each item `in_progress` when starting, `completed` when done. Never batch completions at the end.

---

## Phase 1 — Discovery

Read `~/.copilot/dreamers/templates/discovery-questions.md` and use those questions to grill the user. Conversation only — write nothing to disk yet. Follow the grilling rules in that file. Do not proceed to Phase 2 until every question has a concrete answer.

---

## Phase 2 — Tech stack recommendation

Based on the discovery answers, recommend a stack optimised for scale, fast deployment, AI-assisted development, and operational simplicity. Present it as:

- **Frontend** (if applicable)
- **Backend / API**
- **Database**
- **Auth**
- **Hosting / infra**
- **CI/CD**
- **Testing strategy**
- **AI integration** (if applicable)

For each choice: one-line rationale + rejected alternatives and why.

Call `request_information` with `["Stack approved — write the brief", "Adjust the stack", "Other"]`. On `Adjust` or `Other`, capture corrections, revise the recommendation, re-present. Loop until approved.

---

## Phase 3 — Project brief

Read `~/.copilot/dreamers/templates/project-brief.md`. Fill it out using the discovery answers and agreed stack. Write it to `.dreamers/atlas/project-brief.md` (create the directory if it doesn't exist).

Present the brief to the user in chat, then call `request_information` with `["Brief approved — bootstrap the repo", "Revise the brief", "Other"]`. On `Revise` or `Other`, capture changes, update the brief on disk, re-present. Do not proceed to Phase 4 until explicit approval.

---

## Phase 4 — Repo & workspace bootstrap

Follow `refs/project-bootstrap.md` for checklist.

**Check for existing repo:**
```
git rev-parse --is-inside-work-tree 2>/dev/null
```

If not already a repo:
1. Call `request_information` with `["Public", "Private", "Other"]` to choose repo visibility.
2. Run the following commands inline (no subagent — this is mechanical setup the orchestrator does directly):
   - `git init`
   - `gh repo create [project-name] --[public|private] --source=. --remote=origin`
   - `git remote set-url origin git@github.com:[owner]/[project-name].git`
   - Create `.gitignore` with `.dreamers/` plus standard ignores for the agreed stack
   - Create `.dreamers/plans/` and `.dreamers/atlas/` directories

Then create the project-level `.github/copilot-instructions.md` per `project-bootstrap.md` ownership rules — this requires judgment and is done directly.
---

## Phase 5 — Shell plans

Read `~/.copilot/dreamers/templates/shell-plan.md`. For each milestone in the approved brief, create a shell plan in `.dreamers/plans/` using plan naming rules from `refs/plan-rules.md`.

After writing all plans, list them in chat with file paths and one-line summaries.

---

## Phase 6 — Review loop

Call `request_information` with `["Shell plans look good — I'll take it from here", "Revise the milestones (split / merge / reorder / rescope)", "Other"]`.

- `Look good` → exit this skill; tell the user to invoke `/dreamers-plan` on a specific milestone (or `/dreamers-full` to plan + implement in one session).
- `Revise` or `Other` → capture changes, update affected plan files, re-list all plans, re-call the gate. Repeat until the user signs off.

This skill ends when the user is happy with the shell plans. From there the user invokes `/dreamers-plan` on a specific milestone (or `/dreamers-full` to plan + implement in one session).

