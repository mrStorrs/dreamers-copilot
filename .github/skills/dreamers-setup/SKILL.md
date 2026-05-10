---
name: dreamers-setup
description: 'Prepare the local environment to run the Dreamers bash scripts: detect missing dependencies, propose OS-appropriate install commands, get user approval per command, install, and re-verify with the dep-check script. Triggers: /dreamers-setup, set up dreamers, install dreamers deps, check dreamers environment.'
---

Prepare the local environment for the Dreamers bash scripts (`~/.copilot/dreamers/scripts/dreamers-*.sh`). Run the deterministic dep-check first, then drive any missing-tool installs interactively.

The Dreamers script set is intentionally small — only the LLM-error-prone routines were extracted. Most pipeline work still runs as inline bash inside skills/refs, so the dependency footprint here is essentially the same set Dreamers always required.

Follow the Dreamers Kernel and output discipline from `copilot-instructions.md`.

$ARGUMENTS

---

## Step 1 — Run the dep-check

```bash
~/.copilot/dreamers/scripts/dreamers-deps-check.sh
```

Capture the output. If the final line is `Missing: 0`, report `Environment OK` and **stop**. There is nothing to set up.

Otherwise, parse the `MISSING:` lines into a list of `{tool, needed_by}` pairs. The dep-check tool list (for reference): `bash`, `git`, `gh`, `gh-auth`, `python3`, `sed`, `awk`, `grep`.

## Step 2 — Detect environment

Determine, from this single round of probes (don't trickle):
- **OS / shell** — `uname -a`, plus `[ -n "$WSL_DISTRO_NAME" ]` to detect WSL inside Linux uname.
- **Available package managers** — `command -v` for each candidate:
  - Windows (Git Bash / pwsh): `winget`, `choco`, `scoop`
  - macOS: `brew`, `port`
  - Linux: `apt-get`, `dnf`, `pacman`, `apk`, `zypper`
- **Privilege** — note whether the current shell is elevated (`sudo -n true 2>/dev/null` on POSIX, or pwsh `[Security.Principal.WindowsPrincipal]` admin check on Windows). Do not attempt to escalate yourself.

Pick **one** preferred package manager per OS. If multiple are present, ask the user once with `ask_user` — list them with what each will be used for.

## Step 3 — Propose an install plan, per missing dep

Build a per-tool install command using the detected OS + preferred PM. Reference table:

| Tool | Windows (winget) | Windows (choco) | macOS (brew) | Debian/Ubuntu (apt) | Fedora (dnf) | Arch (pacman) |
|------|------------------|-----------------|--------------|---------------------|--------------|---------------|
| `git` | `winget install --id Git.Git -e` | `choco install git -y` | `brew install git` | `sudo apt-get install -y git` | `sudo dnf install -y git` | `sudo pacman -S --noconfirm git` |
| `gh` | `winget install --id GitHub.cli -e` | `choco install gh -y` | `brew install gh` | `sudo apt-get install -y gh` | `sudo dnf install -y gh` | `sudo pacman -S --noconfirm github-cli` |
| `python3` | `winget install --id Python.Python.3.12 -e` | `choco install python -y` | `brew install python` | `sudo apt-get install -y python3` | `sudo dnf install -y python3` | `sudo pacman -S --noconfirm python` |

**Special cases:**
- **`bash`** — if missing on Windows, the only sensible answer is "install Git for Windows" (`winget install --id Git.Git -e` bundles bash + coreutils). Surface that to the user; do not try to install bash standalone.
- **`gh-auth`** — there is no install command. The user must run `gh auth login` themselves (it is interactive). Surface this with the verbatim command and stop trying to handle it inside this skill.
- **POSIX coreutils** (`sed`, `awk`, `grep`) — on Windows, missing coreutils means Git Bash is incomplete; recommend reinstalling Git for Windows. On Linux/macOS, install via the OS PM (e.g. `coreutils`).
- **`python3` on Windows when the Microsoft Store stub is shadowing real Python** — note this in the proposal; the install command alone won't fix the PATH ordering. Tell the user to either uninstall the Store stub or move real Python ahead of `WindowsApps` in PATH. Note also: `python3` is only required for `dreamers-catalog-lint.sh`, which is a dev-time tool for the dreamers-copilot repo. End users running pipelines do not need Python at all — flag this so the user can choose to skip.

## Step 4 — Confirm each install (gate)

For each proposed install command, call `ask_user` once with the choice `["Install"]` and the exact command shown verbatim. Allow freeform corrections. On rejection, record `skipped` for that tool.

Do not bundle multiple commands behind a single approval. One command, one gate.

## Step 5 — Run approved installs

Execute each approved command. Capture stdout + stderr. For each:
- Success → record `installed`
- Failure → record `failed: <one-line reason>`

If a command needs elevated privileges and the shell is not elevated, do not silently retry — surface the failure with the exact command and tell the user to re-run this skill from an elevated shell.

Never auto-run `sudo` commands without confirmation in the same prompt.

## Step 6 — Re-verify

Re-run the dep-check:
```bash
~/.copilot/dreamers/scripts/dreamers-deps-check.sh
```

Report a final summary:
- `<N>` already OK at start
- `<N>` installed this run
- `<N>` skipped (user rejected)
- `<N>` failed (with reasons)
- `<N>` require manual user action (e.g. `gh auth login`, PATH fix)

If `Missing: 0` after the re-check, end with `Environment OK`. Otherwise end with `Environment incomplete — N items remain` and list them.

## Constraints

- **Never install without explicit per-command user approval.**
- **Never run `gh auth login` automatically** — it is interactive and credential-bearing; surface it for the user.
- **Never modify `git config`.** Per `~/.copilot/instructions/git.instructions.md`.
- **Never silently escalate privileges.** If `sudo` or admin pwsh is required and the shell isn't elevated, stop and tell the user.
- **Never disable or skip the final dep-check.** It is the only source of truth for "done".
