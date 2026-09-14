# Dreamers

A compact workflow for GitHub Copilot CLI, designed around simplicity, correctness, and explicit steps suitable for GPT-5.6 Luna.

## Delivery

    /dreamers add offline export
    /dreamers add offline export --plan
    /dreamers feature-search/plan-01-indexing.md
    /dreamers feature-search/manifest.md

Task input follows: Grill → proposal approval → save proposal as plan → implementation → Vigil → fixes → required user testing → docs and close-out → approved PR.

Approving the proposal starts implementation immediately. Detailed plans are opt-in through --plan or /dreamers-plan. Existing proposals, detailed plans, and manifests can be supplied directly. The full Grill transcript stays beside the plan; agents consult it when needed instead of receiving it in every prompt.

Retrospectives, improvement logs, and test timing records remain mandatory. Scope changes, triggered manual testing, and PR creation retain their approval gates. Tests must verify meaningful behavior and survive harmless refactors; tests-first is optional.

## Commands

| Command | Purpose |
| --- | --- |
| /dreamers-help | Orientation and examples |
| /dreamers-plan | Detailed planning only |
| /dreamers-implement | Implement an approved proposal or plan |
| /dreamers-lite | Bounded bug fix with meaningful verification |
| /dreamers-review | Review through Vigil; report without fixes |
| /dreamers-test, /dreamers-simplify | Focused Vigil audits |
| /dreamers-find-refactors | Section audits and candidate plans |
| /dreamers-docs | Echo documentation update |
| /dreamers-pr, /dreamers-pr-resolve | PR creation and feedback |
| /dreamers-research, /dreamers-explain | Research or focused explanation |
| /dreamers-issue, /dreamers-new-project | Issue creation and project bootstrap |
| /dreamers-add-logging | Logging audit and approved changes |
| /dreamers-cleanup-comments, /dreamers-cleanup-comments-branch | Approved comment cleanup |
| /dreamers-clean-work, /dreamers-plan-verify | Maintenance and drift checks |
| /dreamers-update | Copilot changes, then explicitly approved Codex transfer |

## Agents and review

Vigil is the automatic code reviewer for every plan depth and for planless reviews. Sentinel, Probe, and Hone remain available only on explicit user request:

    /dreamers-review --full
    /dreamers-review --lens hone
    /dreamers-review --lenses sentinel,probe

Plan complexity and generated plan text cannot select extra reviewers. Reviews write one artifact per reviewer and end by answering **How could I make this code simpler?** The orchestrator evaluates suggestions, preserves correctness, and asks before expanding scope.

Echo updates docs; Sage researches. Forge and Nova are user-entered implementation/planning personas. Agents inherit the selected session model instead of pinning a more expensive model. See [Copilot agent configuration](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agent-frontmatter-fields).

## Package layout

- .github/skills/: entry points with explicit phase steps.
- .github/agents/: role definitions.
- .github/instructions/: shared execution, code, and comment rules.
- .github/dreamers/refs/ and templates/: canonical shared rules and artifact formats.

Forge and /dreamers-implement are the first two entry points restored to synchronized XML blocks. Their shared Dreamers rules are embedded before installation, so execution does not depend on reading reference/template files. Code and comment instruction files use the same canonical sources. Other entry points still use linked rules while this two-entry-point revision is evaluated.

Edit shared rules in `.github/dreamers/refs/<name>.md` and run the sync command below. Consumers declare a block with `<name>` and `</name>`, each on its own line at column zero. Keep workflow-specific steps outside those blocks. Project instructions, approved plans, and verification artifacts remain runtime inputs.

Local work lives in gitignored .dreamers/. Root test-benchmarks.md records successful test durations; defered.md records explicit user deferrals.

## Install and upgrade

Requires PowerShell 7:

    pwsh -File ./Install-Dreamers.ps1
    pwsh -File ./Install-Dreamers.ps1 -Force
    pwsh -File ./Install-Dreamers.ps1 -CopilotHome /custom/copilot

The default target is ~/.copilot/. Use -Force to upgrade all managed files and remove retired references. Without -Force, existing files and legacy dependencies are retained. Personal instructions and unrelated files are preserved.

Shared rules use the .instructions.md suffix required by [Copilot instruction discovery](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions). Upgrades replace the old dreamers.laws.md name. The retired /dreamers-full has no alias.

## Remove

    pwsh -File ./Remove-Dreamers.ps1 -DryRun
    pwsh -File ./Remove-Dreamers.ps1
    pwsh -File ./Remove-Dreamers.ps1 -CopilotHome /custom/copilot

Removal includes known retired managed files and preserves unrelated files.

## Maintain and verify

    ./scripts/sync-refs.sh -Sync
    ./scripts/sync-refs.sh -Verify
    ./scripts/Test-DreamersCopilot.sh

Or with PowerShell:

    pwsh -File ./scripts/sync-refs.ps1 -Sync
    pwsh -File ./scripts/sync-refs.ps1 -Verify
    pwsh -File ./scripts/Test-DreamersCopilot.ps1

Sync replaces declared XML regions with their canonical reference content. Reference names and content match case-sensitively. Keep reference blocks separate; nested references overlap replacement regions and are rejected. Verify reports drift without writing. Malformed marker pairs stop synchronization before any files are changed. The Bash sync command requires Python 3.

Both package test commands run the same PowerShell validator. It checks XML drift, package metadata, catalog targets, links, and real install/upgrade/removal behavior in a temporary target. Synthetic sync cases cover exact content replacement, surrounding-content preservation, idempotence, and refusing malformed batches without partial writes. Linux exercises both sync implementations; Windows exercises PowerShell. Installer cases protect personal files, non-force behavior, idempotence, and DryRun. These checks exercise tooling behavior; they do not assert prompt wording. Use -SkipInstallSmoke for structural checks, including XML drift, without temporary behavior fixtures.

For a consuming project, follow [bootstrap rules](.github/dreamers/refs/project-bootstrap.md). For system maintenance, update the relevant rules, entry points, and docs together.
