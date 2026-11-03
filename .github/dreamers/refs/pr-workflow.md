**Input:** committed feature branch, delivery and validation summary, optional shipped plan paths, and optional `--issue <#|url>`. Enter only when publishing is authorized. Apply the embedded `dreamers-kernel`, `git-workflow`, and `pr-description` rules.

**1. Verify**

- `git status` — confirm clean (no unstaged/untracked production files).
- `git log --oneline -10` — confirm commit history matches expectation.
- Detect default branch (canonical two-step per `git-workflow`, Kernel).

**2. Push**

- `git push -u origin <branch>` — never force; never skip hooks.
- If push is rejected (non-fast-forward): `git fetch origin` + rebase + re-push. Never force.

**3. Open the PR**

- Draft the PR body using the embedded `pr-description` format.
- `gh pr create --base "$DEFAULT_BRANCH" --head <branch> --title "<short title>" --body <body>`. Capture PR URL.
- If `--issue <#|url>`: `gh issue comment <#> --body "Resolved in <PR URL>"` (do NOT close until merge).

**4. Archive shipped plans**

- If this PR ships a Dreamers plan from `.dreamers/plans/feature-<slug>/`, archive after the PR is created.
- Single-plan feature directory: move `.dreamers/plans/feature-<slug>/` to `.dreamers/plans/archive/feature-<slug>/`.
- Multi-plan feature directory or manifest sequence: create `.dreamers/plans/archive/feature-<slug>/` if needed, move only the shipped `plan-NN-*.md` file(s) into it, and leave unfinished plans in the live feature directory.
- If `manifest.md` exists, keep it live while any unfinished plan file remains. After the last unfinished plan ships, move `manifest.md` into the same archive directory and remove the now-empty live feature directory.
- If no feature directory applies, skip this step.

**Result:** PR URL and any moved archive paths.
