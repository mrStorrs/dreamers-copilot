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
