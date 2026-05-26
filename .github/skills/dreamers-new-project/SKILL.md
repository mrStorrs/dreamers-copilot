---
name: dreamers-new-project
description: 'Bootstrap a brand new project from scratch: discovery questions, project brief, shell plans. Triggers: /dreamers-new-project, new project, bootstrap a project, start a new project.'
argument-hint: '(no args; discovery is conversational)'
---

Bootstrap a brand new project from scratch. Work through the phases in order. Do not skip ahead or write anything permanent until the user explicitly approves the brief.

Follow the Dreamers Kernel and output discipline from `~/.copilot/copilot-instructions.md`.

## Inlined ref content

Refs below are inlined from `.github/dreamers/refs/` by `scripts/sync-refs.ps1`. Do NOT edit between the XML tags — edit the source file and re-run sync.


<project-bootstrap>
# Project Bootstrap

## Bootstrap checklist for new repos
1. Ensure `.dreamers/` is in the project's `.gitignore`
2. Create the project-level `.github/copilot-instructions.md` (see ownership below)
3. Create `.dreamers/plans/` directory
4. Install instruction files to `.github/instructions/`:
   - Copy `comment-rules.instructions.md` from the Dreamers repo's `.github/instructions/` directory into `.github/instructions/` at the project root. This auto-injects comment rules whenever Copilot touches source files.
5. **Optional but recommended. (Ask user if they want this created or not):** create `.github/instructions/build.instructions.md` if the project has a defined build/distribution flow for test builds. The file is the authoritative playbook the orchestrator follows during user-testing pauses. It should specify:
   - Which commands (if any) the orchestrator is authorised to run itself
   - Which steps must be performed by the user (install on device, launch app, version/build number to verify, etc.)
   - Where the build artifact lives (link, path, store listing) and how to fetch it
   - How to recover from a failed build/distribution
   If this file is absent, the orchestrator will pause user-testing rounds and ask the user to build/distribute manually.

## Project copilot-instructions.md ownership (split)

The project-level `.github/copilot-instructions.md` is the shared briefing all agents read on startup.

**Skill/orchestrator owns (initial creation + ongoing):**
- **Constraints** — anything agents must never do (e.g., no direct DB writes, no breaking public API)
- **Distribution** — short pointer to `.github/instructions/build.instructions.md` if it exists (the authoritative playbook), or a brief note that the orchestrator should ask the user to build/distribute when no playbook is present
- **Links** — plan directory, global workspace, related repos

**Echo owns (updated after each cycle):**
- **Tech stack** — languages, frameworks, major dependencies
- **Repo structure** — key directories and what lives where
- **Conventions** — naming, formatting, branching, commit style, test commands
- **Key files** — entry points, config files, CI/CD definitions

Do not touch Echo-owned sections during orchestration — those updates come from Echo after each cycle.
</project-bootstrap>


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

