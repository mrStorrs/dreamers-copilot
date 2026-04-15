---
name: dreamers-new-project
description: 'Bootstrap a brand new project from scratch: discovery questions, project brief, shell plans. Triggers: /dreamers-new-project, new project, bootstrap a project, start a new project.'
---

Bootstrap a brand new project from scratch. Work through the phases in order. Do not skip ahead or write anything permanent until the user explicitly approves the brief.

Read these refs:
- `~/.copilot/dreamers/refs/project-bootstrap.md`
- `~/.copilot/dreamers/refs/plan-rules.md`

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

$ARGUMENTS

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

Ask: "Does this stack work, or do you want to adjust anything before we write the brief?" Iterate until agreed.

---

## Phase 3 — Project brief

Read `~/.copilot/dreamers/templates/project-brief.md`. Fill it out using the discovery answers and agreed stack. Write it to `.dreamers/atlas/project-brief.md` (create the directory if it doesn't exist).

Present the brief to the user in chat. Ask explicitly: **"Does this brief accurately capture the project? Approve or tell me what to change."**

Do not proceed to Phase 4 until the user explicitly approves.

---

## Phase 4 — Repo & workspace bootstrap

Follow `refs/project-bootstrap.md` for checklist.

**Check for existing repo:**
```
git rev-parse --is-inside-work-tree 2>/dev/null
```

If not already a repo:
1. Ask the user: public or private repo?
2. Invoke **Bolt** with the following commands:
   - `git init`
   - `gh repo create [project-name] --[public|private] --source=. --remote=origin`
   - `git remote set-url origin git@github.com:[owner]/[project-name].git`
   - Create `.gitignore` with `.dreamers/` plus standard ignores for the agreed stack
   - `mkdir -p .dreamers/plans .dreamers/atlas`

After Bolt completes, create the project-level `CLAUDE.md` per project-bootstrap.md ownership rules (this requires judgment — do it directly, not via Bolt).

---

## Phase 5 — Shell plans

Read `~/.copilot/dreamers/templates/shell-plan.md`. For each milestone in the approved brief, create a shell plan in `.dreamers/plans/` using plan naming rules from `refs/plan-rules.md`.

After writing all plans, list them in chat with file paths and one-line summaries.

---

## Phase 6 — Review loop

Ask the user: **"Review the milestone breakdown above. Tell me if you want to split, merge, reorder, or rescope any milestone. When you're satisfied, call `/dreamers-full` on whichever milestone you want to start with."**

If the user requests changes: update the affected plan files, re-list all plans, and ask again. Repeat until the user signs off.

Do not invoke Forge, Sentinel, or Probe. This skill ends when the user is happy with the shell plans.

