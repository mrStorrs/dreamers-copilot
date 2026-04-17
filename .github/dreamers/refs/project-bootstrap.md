# Project Bootstrap

## Bootstrap checklist for new repos
1. Ensure `.dreamers/` is in the project's `.gitignore`
2. Create the project-level `CLAUDE.md` (see ownership below)
3. Create `.dreamers/plans/` directory
4. Install instruction files to `.github/instructions/`:
   - Copy `comment-rules.instructions.md` from the Dreamers repo's `.github/instructions/` directory into `.github/instructions/` at the project root. This auto-injects comment rules whenever Copilot touches source files.

## Project CLAUDE.md ownership (split)

The project-level `CLAUDE.md` at the repo root is the shared briefing all agents read on startup.

**Skill/orchestrator owns (initial creation + ongoing):**
- **Constraints** — anything agents must never do (e.g., no direct DB writes, no breaking public API)
- **Distribution** — how to build and distribute a test build
- **Links** — plan directory, global workspace, related repos

**Echo owns (updated after each cycle):**
- **Tech stack** — languages, frameworks, major dependencies
- **Repo structure** — key directories and what lives where
- **Conventions** — naming, formatting, branching, commit style, test commands
- **Key files** — entry points, config files, CI/CD definitions

Do not touch Echo-owned sections during orchestration — those updates come from Echo after each cycle.
