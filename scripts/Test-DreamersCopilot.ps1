[CmdletBinding()]
param(
    [string]$Root = $(if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }),
    [switch]$SkipInstallSmoke
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
    param([string]$Message)
    $script:errors.Add($Message)
}

function Assert-ExactSet {
    param(
        [string]$Label,
        [string[]]$Expected,
        [string[]]$Actual
    )
    foreach ($item in ($Expected | Where-Object { $_ -notin $Actual })) {
        Add-Error "Missing $Label item: $item"
    }
    foreach ($item in ($Actual | Where-Object { $_ -notin $Expected })) {
        Add-Error "Unexpected $Label item: $item"
    }
}

function Assert-Path {
    param([string]$Path, [string]$Label)
    if (-not (Test-Path $Path)) {
        Add-Error "Missing $Label at $Path"
    }
}

function Assert-Patterns {
    param(
        [string]$Path,
        [hashtable]$Patterns
    )
    if (-not (Test-Path $Path)) {
        Add-Error "Missing contract file: $Path"
        return
    }
    $content = Get-Content -Raw $Path
    $options = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor
        [System.Text.RegularExpressions.RegexOptions]::Multiline -bor
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    foreach ($entry in $Patterns.GetEnumerator()) {
        if (-not [regex]::IsMatch($content, [string]$entry.Value, $options)) {
            Add-Error "Missing $($entry.Key) contract in $Path"
        }
    }
}

function Assert-NoPatterns {
    param(
        [string]$Path,
        [hashtable]$Patterns
    )
    if (-not (Test-Path $Path)) {
        Add-Error "Missing contract file: $Path"
        return
    }
    $content = Get-Content -Raw $Path
    $options = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase -bor
        [System.Text.RegularExpressions.RegexOptions]::Multiline -bor
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    foreach ($entry in $Patterns.GetEnumerator()) {
        if ([regex]::IsMatch($content, [string]$entry.Value, $options)) {
            Add-Error "Unexpected $($entry.Key) contract in $Path"
        }
    }
}

function Assert-SynchronizedRefs {
    $refsRoot = Join-Path $Root ".github/dreamers/refs"
    $refs = @{}
    foreach ($ref in Get-ChildItem $refsRoot -Filter "*.md" -File) {
        $content = Get-Content -Raw $ref.FullName
        if ($null -eq $content) { $content = "" }
        $content = $content.Replace(([string][char]13 + [char]10), [string][char]10).Replace([string][char]13, [string][char]10)
        $refs[$ref.BaseName] = $content.TrimEnd([char]10)
    }
    foreach ($consumer in Get-ChildItem (Join-Path $Root ".github") -Filter "*.md" -File -Recurse) {
        if ($consumer.FullName.StartsWith($refsRoot + [System.IO.Path]::DirectorySeparatorChar)) {
            continue
        }
        $content = Get-Content -Raw $consumer.FullName
        if ($null -eq $content) { $content = "" }
        $content = $content.Replace(([string][char]13 + [char]10), [string][char]10).Replace([string][char]13, [string][char]10)
        foreach ($name in $refs.Keys) {
            $escapedName = [regex]::Escape($name)
            $pattern = "(?ms)^<$escapedName>\n(.*?)\n</$escapedName>"
            $match = [regex]::Match($content, $pattern)
            if ($match.Success -and $match.Groups[1].Value -ne $refs[$name]) {
                Add-Error "Synchronized ref drift in $($consumer.FullName): $name"
            }
        }
    }
}

$expectedAgents = @("echo", "forge", "hone", "nova", "probe", "sage", "sentinel", "vigil")
$expectedSkills = @(
    "dreamers",
    "dreamers-add-logging",
    "dreamers-clean-work",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-docs",
    "dreamers-find-refactors",
    "dreamers-lite",
    "dreamers-implement",
    "dreamers-issue",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-plan-verify",
    "dreamers-pr",
    "dreamers-pr-resolve",
    "dreamers-research",
    "dreamers-review",
    "dreamers-simplify",
    "dreamers-test",
    "dreamers-update"
)
$expectedRefs = @(
    "agent-recovery.md",
    "comment-rules.md",
    "dreamers-kernel.md",
    "git-workflow.md",
    "hone-architecture-rubric.md",
    "logging-discipline.md",
    "planning-grill.md",
    "project-bootstrap.md",
    "reviewer-findings-format.md",
    "testing-mandate.md"
)
$expectedTemplates = @(
    "discovery-questions.md",
    "github-issue.md",
    "logging-standards.md",
    "manifest.md",
    "plan-guide-complex.md",
    "plan-guide-lite.md",
    "plan-guide-selector.md",
    "plan-guide-standard.md",
    "plan.md",
    "pr-description.md",
    "project-brief.md",
    "shell-plan.md",
    "test-benchmarks.md",
    "user-testing-gate.md"
)
$expectedInstructions = @(
    "dreamers.comment-rules.instructions.md",
    "dreamers.instructions.md",
    "dreamers.laws.md"
)
$expectedSkillReadmes = @(
    "dreamers",
    "dreamers-add-logging",
    "dreamers-cleanup-comments",
    "dreamers-cleanup-comments-branch",
    "dreamers-find-refactors",
    "dreamers-lite",
    "dreamers-implement",
    "dreamers-new-project",
    "dreamers-plan",
    "dreamers-pr-resolve",
    "dreamers-research",
    "dreamers-review"
)

$agentRoot = Join-Path $Root ".github/agents"
$skillRoot = Join-Path $Root ".github/skills"
$dreamersRoot = Join-Path $Root ".github/dreamers"
$instructionsRoot = Join-Path $Root ".github/instructions"

Assert-Path $agentRoot "agents directory"
Assert-Path $skillRoot "skills directory"
Assert-Path $dreamersRoot "dreamers directory"
Assert-Path $instructionsRoot "instructions directory"

if (Test-Path $agentRoot) {
    $actualAgents = Get-ChildItem $agentRoot -Filter "*.agent.md" -File |
        ForEach-Object { $_.Name -replace "\.agent\.md$", "" }
    Assert-ExactSet -Label "agent" -Expected $expectedAgents -Actual $actualAgents
}

if (Test-Path $skillRoot) {
    $actualSkills = Get-ChildItem $skillRoot -Directory | ForEach-Object { $_.Name }
    Assert-ExactSet -Label "skill" -Expected $expectedSkills -Actual $actualSkills
    foreach ($skillName in $expectedSkills) {
        $skillFile = Join-Path (Join-Path $skillRoot $skillName) "SKILL.md"
        if (-not (Test-Path $skillFile)) {
            Add-Error "Missing SKILL.md: $skillFile"
            continue
        }
        $content = Get-Content -Raw $skillFile
        $frontmatter = [regex]::Match($content, "(?s)^---\s*\n(.*?)\n---")
        if (-not $frontmatter.Success) {
            Add-Error "Invalid frontmatter: $skillFile"
            continue
        }
        $name = [regex]::Match($frontmatter.Groups[1].Value, '(?m)^name:\s*[''"]?([^''"\n]+)')
        if (-not $name.Success -or $name.Groups[1].Value.Trim() -ne $skillName) {
            Add-Error "Skill name does not match directory: $skillFile"
        }
        if ($frontmatter.Groups[1].Value -notmatch "(?m)^description:\s*.+$") {
            Add-Error "Skill missing description: $skillFile"
        }
    }
    foreach ($skillName in $expectedSkillReadmes) {
        $readme = Join-Path (Join-Path $skillRoot $skillName) "readme.md"
        if (-not (Test-Path $readme)) {
            Add-Error "Missing skill readme: $readme"
        }
    }
}

foreach ($entry in @(
    @{ Label = "ref"; Path = (Join-Path $dreamersRoot "refs"); Expected = $expectedRefs },
    @{ Label = "template"; Path = (Join-Path $dreamersRoot "templates"); Expected = $expectedTemplates },
    @{ Label = "instruction"; Path = $instructionsRoot; Expected = $expectedInstructions }
)) {
    if (Test-Path $entry.Path) {
        $actual = Get-ChildItem $entry.Path -File | ForEach-Object { $_.Name }
        Assert-ExactSet -Label $entry.Label -Expected $entry.Expected -Actual $actual
    }
}

$catalogPath = Join-Path $Root ".github/catalog.json"
Assert-Path $catalogPath "catalog"
if (Test-Path $catalogPath) {
    try {
        $catalog = Get-Content -Raw $catalogPath | ConvertFrom-Json
        $items = @($catalog.items | ForEach-Object { "$($_.type):$($_.slug)" })
        foreach ($required in @("skill:dreamers")) {
            if ($required -notin $items) { Add-Error "Catalog missing item: $required" }
        }
        foreach ($retired in @("skill:dreamers-full")) {
            if ($retired -in $items) { Add-Error "Catalog retains retired item: $retired" }
        }
        foreach ($item in $catalog.items) {
            if ($item.path -and -not (Test-Path (Join-Path $Root $item.path))) {
                Add-Error "Catalog item path does not exist: $($item.path)"
            }
        }
        foreach ($collection in $catalog.collections) {
            $members = @($collection.members | ForEach-Object { "$($_.type):$($_.slug)" })
            foreach ($required in @("skill:dreamers")) {
                if ($required -notin $members) { Add-Error "Collection missing member: $required" }
            }
            foreach ($retired in @("skill:dreamers-full")) {
                if ($retired -in $members) { Add-Error "Collection retains retired member: $retired" }
            }
        }
    }
    catch {
        Add-Error "Invalid catalog JSON: $($_.Exception.Message)"
    }
}

Assert-Patterns (Join-Path $skillRoot "dreamers/SKILL.md") @{
    "missing-input halt" = 'If no task description, plan path, or manifest was provided, halt \+ ask'
    "three input modes" = '## Modes.*Task description.*Plan path\(s\).*manifest\.md'
    "artifact modes skip start gate" = 'Plan path mode:.*Do not invoke `/dreamers-plan`.*Manifest mode:.*Do not invoke `/dreamers-plan`'
    "startup contract loading" = 'Before reading `\.dreamers/` files, read and apply.*dreamers-kernel\.md.*git-workflow\.md.*startup verification'
    "branch setup" = 'Branch setup once per `git-workflow`:.*checkout.*pull.*feat/<slug>'
    "plan quality" = 'Plan quality check.*Plan-type.*plan-guide-selector'
    "planning delegation" = '## Phase 1.*Invoke `/dreamers-plan \$ARGUMENTS`'
    "single-plan implementation-start gate" = 'Approved — start implementation.*Revise plan.*Halt.*Other'
    "multi-plan implementation-start gate" = 'Approved — start INCREMENTAL.*Approved — start ATOMIC.*Revise plan.*Halt.*Other'
    "implementation then review" = '### Steps 1.3.*Invoke `/dreamers-implement.*### Step 4.*Invoke `/dreamers-review'
    "complexity review delegation" = '/dreamers-review` selects Vigil, Sentinel \+ Probe, or Sentinel \+ Probe \+ Hone from plan complexity or explicit plan/user direction'
    "major-refactor gate" = 'Major-refactor gate.*Apply now.*Defer — save to defered\.md.*Other'
    "deferred findings ledger" = 'Defer.*do NOT apply or create a follow-up plan.*defered\.md.*# Deferred Suggestions.*never overwrite.*Stage `defered\.md`'
    "major-change rerun gate" = 'Run Vigil.*Run full triad.*Run selected /dreamers-review lane.*Skip reviewer rerun.*Other'
    "templated user testing" = 'user-testing-gate\.md.*Testing steps.*Notes.*Approved.*Bug found \(enter text\).*Other \(enter text\)'
    "incremental close-out" = 'INCREMENTAL.*Invoke `/dreamers-docs --branch`.*Pre-PR approval gate.*Invoke `/dreamers-pr`'
    "atomic continuation" = 'ATOMIC.*Do NOT push'
    "full close-out" = 'Phase 3.*improvements\.md.*Invoke `/dreamers-docs --branch`.*Write retro.*Final commit.*User approval gate.*Invoke `/dreamers-pr`'
}
Assert-Patterns (Join-Path $skillRoot "dreamers-pr-resolve/SKILL.md") @{
    "deferred Vigil findings ledger" = 'Defer — save to defered\.md.*do NOT apply.*create a follow-up plan.*defered\.md.*# Deferred Suggestions.*never overwrite.*Stage `defered\.md`'
    "deferred ledger commit" = 'If any fixes landed or Step 5 added deferred entries'
    "deferred ledger report" = 'Deferred Vigil findings recorded in `defered\.md`'
}
Assert-NoPatterns (Join-Path $skillRoot "dreamers/SKILL.md") @{
    "inline implementation heading" = "## Implement each plan inline"
    "retired plan verification phase" = "invoke\s+`?/dreamers-plan-verify"
    "help route" = "--help"
    "Grill opt-out" = "--no-grill|do not grill|skip the interview"
    "separate review-selection policy" = "<review-selection>|danger rubric|low-risk lite or standard"
    "conditional milestone close-out" = "triggered retrospective|retrospective need|documentation need"
    "implementation-only synchronized refs" = "<(planning-grill|testing-mandate|comment-rules|logging-discipline|reviewer-findings-format|agent-recovery)>"
}
Assert-Patterns (Join-Path $skillRoot "dreamers-implement/SKILL.md") @{
    "tests-first implementation" = "failing tests.*implement|tests.first"
    "type-check and tests" = "Step 3 — Type-check \+ run tests.*type-check \+ test command"
    "bounded validation attempts" = "max 3 attempts"
    "benchmark updates" = "test-benchmarks\.md.*after passing"
    "green exit" = 'Return the AC coverage matrix at green tests.*invokes `/dreamers-review` immediately'
    "phase boundary" = "Do not invoke reviewers.*user testing.*commit.*push.*PR creation"
    "conditional todo ownership" = "When standalone.*todo.*When invoked by an outer delivery skill.*existing todo"
}
Assert-NoPatterns (Join-Path $skillRoot "dreamers-implement/SKILL.md") @{
    "stale seven-step todo" = "Step 5 \(review\).*Step 6 \(user test\).*Step 7 \(commit\)"
}
Assert-Patterns (Join-Path $skillRoot "dreamers-review/SKILL.md") @{
    "Vigil execution mode" = "--vigil.*Vigil|Vigil.*--vigil"
    "full execution mode" = "--full.*Sentinel \+ Probe \+ Hone"
    "selection precedence" = "explicit lane flag or explicit user direction.*explicit reviewer requirement.*Plan-type"
    "lite selection" = 'lite` = Vigil'
    "standard selection" = 'standard` = Sentinel \+ Probe'
    "complex selection" = 'complex` = Sentinel \+ Probe \+ Hone'
    "planless intent inference" = "infer the intended behavior.*explicit user direction.*PR title/body.*commits and diff.*changed tests.*changed code"
    "planless ambiguity question" = "one reliable interpretation.*ask the user one concise question"
    "planless reviewer basis" = "review basis.*absolute plan path.*inferred-intent summary"
    "conditional todo ownership" = "when standalone.*todo.*when invoked by an outer delivery skill.*existing todo"
    "project-file read-only boundary" = "read.only.*project (code|files)|project (code|files).*read.only"
    "reviewer artifact-only writes" = "reviewer.*(only|sole).*write.*artifact|reviewer.*write.*exactly one.*artifact"
    "caller owns fix loop" = "caller owns all finding disposition, gates, fixes, revalidation, and user testing"
}
Assert-Patterns (Join-Path $agentRoot "vigil.agent.md") @{
    "planless Vigil review basis" = "If no plan is bound.*inferred-intent summary.*evidence"
    "planless Vigil requirements" = "plan AC or inferred requirement"
}
Assert-Patterns (Join-Path $agentRoot "probe.agent.md") @{
    "planless Probe review basis" = "no plan is bound.*inferred requirements"
    "planless Probe findings" = "report missing or weak coverage as findings"
}
Assert-Patterns (Join-Path $instructionsRoot "dreamers.instructions.md") @{
    "same-context skill invocation" = "skill.*same orchestrator context|same orchestrator context.*skill"
    "outermost todo ownership" = "outermost skill.*owns.*todo|todo.*owned by.*outermost skill"
    "global deferred suggestions ledger" = 'Deferred suggestions.*explicitly chooses `Defer`.*defered\.md.*# Deferred Suggestions.*never overwrite.*Stage `defered\.md`'
}
Assert-NoPatterns (Join-Path $skillRoot "dreamers-update/SKILL.md") @{
    "implementation mirror rule" = "dreamers-implement mirror"
}
Assert-Patterns (Join-Path $dreamersRoot "refs/planning-grill.md") @{
    "relentless interview" = "Interview me relentlessly"
    "codebase exploration" = "answered by exploring the codebase, explore"
    "one blocking question" = "Ask one blocking question at a time"
    "three choices" = "recommended answer.*strongest viable alternate.*Other"
}
Assert-Patterns (Join-Path $skillRoot "dreamers-plan/SKILL.md") @{
    "conditional todo ownership" = "When standalone.*todo.*When invoked by an outer delivery skill.*existing todo"
    "invoked return boundary" = "When standalone, hard stop; when invoked by an outer delivery skill, return control"
}
Assert-Patterns (Join-Path $skillRoot "dreamers-new-project/SKILL.md") @{
    "existing-solutions opt-in gate" = "Phase 1\.5.*request_information.*Research similar existing solutions.*Skip research"
    "research blocked before approval" = "Do not perform research before the user explicitly approves it"
    "research remains conversation-only" = "Keep this phase conversation-only: no subagent and no disk writes"
    "research informs downstream artifacts" = "existing-solutions research.*stack recommendation.*project brief"
}

foreach ($path in @(
    (Join-Path $skillRoot "dreamers/SKILL.md"),
    (Join-Path $skillRoot "dreamers-plan/SKILL.md"),
    (Join-Path $skillRoot "dreamers-plan/readme.md"),
    (Join-Path $dreamersRoot "refs/planning-grill.md"),
    (Join-Path $agentRoot "nova.agent.md"),
    (Join-Path $Root "README.md"),
    (Join-Path $Root ".github/README.md")
)) {
    Assert-NoPatterns $path @{
        "Grill opt-out policy" = "--no-grill|do not grill|skip the interview"
    }
}

Assert-SynchronizedRefs

$legacyPattern = "dreamers-full"
$migrationPattern = "retir|remov|legacy|migrat|cleanup|clean up|previous|old command|no longer"
$scanRoots = @(
    $agentRoot,
    $skillRoot,
    $dreamersRoot,
    $instructionsRoot,
    (Join-Path $Root "README.md"),
    (Join-Path $Root ".github/README.md"),
    $catalogPath
) | Where-Object { Test-Path $_ }
foreach ($scanRoot in $scanRoots) {
    $files = if ((Get-Item $scanRoot).PSIsContainer) {
        Get-ChildItem $scanRoot -File -Recurse | Where-Object { $_.Extension -in @(".md", ".json", ".ps1") }
    } else {
        Get-Item $scanRoot
    }
    foreach ($file in $files) {
        if ($file.Name -like "Test-DreamersCopilot*") { continue }
        $lineNumber = 0
        foreach ($line in Get-Content $file.FullName) {
            $lineNumber++
            if ($line -match $legacyPattern -and $line -notmatch $migrationPattern) {
                Add-Error "Active retired-pipeline reference in $($file.FullName):$lineNumber"
            }
        }
    }
}

if (-not $SkipInstallSmoke) {
    $tmpHome = Join-Path ([System.IO.Path]::GetTempPath()) ("dreamers-copilot-test-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $tmpHome -Force | Out-Null
    try {
        $userInstruction = Join-Path $tmpHome "instructions\user-owned.md"
        $staleCommentRules = Join-Path $tmpHome "instructions\comment-rules.instructions.md"
        $staleGitInstructions = Join-Path $tmpHome "instructions\git.instructions.md"
        foreach ($path in @($userInstruction, $staleCommentRules, $staleGitInstructions)) {
            New-Item -ItemType Directory -Path (Split-Path $path -Parent) -Force | Out-Null
            Set-Content -Path $path -Value "preserve or remove by ownership" -Encoding utf8NoBOM
        }
        $activeLite = Join-Path $tmpHome "skills/dreamers-lite"
        $legacyFull = Join-Path $tmpHome "skills/dreamers-full"
        foreach ($directory in @($activeLite, $legacyFull)) {
            New-Item -ItemType Directory -Path $directory -Force | Out-Null
            Set-Content -Path (Join-Path $directory "SKILL.md") -Value "managed" -Encoding utf8NoBOM
            Set-Content -Path (Join-Path $directory "readme.md") -Value "managed" -Encoding utf8NoBOM
        }
        Set-Content -Path (Join-Path $activeLite "user-owned.md") -Value "preserve" -Encoding utf8NoBOM

        & (Join-Path $Root "Install-Dreamers.ps1") -CopilotHome $tmpHome -Force | Out-Null

        foreach ($path in @(
            (Join-Path $tmpHome "skills/dreamers/SKILL.md"),
            (Join-Path $activeLite "SKILL.md"),
            (Join-Path $activeLite "readme.md"),
            (Join-Path $tmpHome "instructions\dreamers.comment-rules.instructions.md"),
            (Join-Path $tmpHome "instructions\dreamers.laws.md")
        )) {
            if (-not (Test-Path $path)) { Add-Error "Install smoke missing managed file: $path" }
        }
        foreach ($path in @($staleCommentRules, $staleGitInstructions)) {
            if (Test-Path $path) { Add-Error "Install smoke retained obsolete managed file: $path" }
        }
        if (-not (Test-Path $userInstruction)) {
            Add-Error "Install smoke removed user-owned instruction: $userInstruction"
        }
        foreach ($managed in @("SKILL.md", "readme.md")) {
            $path = Join-Path $legacyFull $managed
            if (Test-Path $path) { Add-Error "Install smoke retained legacy managed file: $path" }
        }
        if (-not (Test-Path (Join-Path $activeLite "user-owned.md"))) {
            Add-Error "Install smoke removed user-owned active file: $activeLite"
        }
        if (Test-Path $legacyFull) {
            Add-Error "Install smoke did not prune empty legacy directory: $legacyFull"
        }

        New-Item -ItemType Directory -Path $legacyFull -Force | Out-Null
        Set-Content -Path (Join-Path $legacyFull "SKILL.md") -Value "managed" -Encoding utf8NoBOM
        Set-Content -Path (Join-Path $legacyFull "readme.md") -Value "managed" -Encoding utf8NoBOM
        Set-Content -Path $staleCommentRules -Value "managed" -Encoding utf8NoBOM
        Set-Content -Path $staleGitInstructions -Value "managed" -Encoding utf8NoBOM
        & (Join-Path $Root "Remove-Dreamers.ps1") -CopilotHome $tmpHome | Out-Null

        foreach ($path in @(
            (Join-Path $tmpHome "skills/dreamers/SKILL.md"),
            (Join-Path $tmpHome "instructions\dreamers.comment-rules.instructions.md"),
            (Join-Path $tmpHome "instructions\dreamers.laws.md")
        )) {
            if (Test-Path $path) { Add-Error "Remove smoke retained managed file: $path" }
        }
        foreach ($path in @($staleCommentRules, $staleGitInstructions)) {
            if (Test-Path $path) { Add-Error "Remove smoke retained obsolete managed file: $path" }
        }
        if (-not (Test-Path $userInstruction)) {
            Add-Error "Remove smoke removed user-owned instruction: $userInstruction"
        }
        if (-not (Test-Path (Join-Path $activeLite "user-owned.md"))) {
            Add-Error "Remove smoke removed user-owned active file: $activeLite"
        }
        if (Test-Path $legacyFull) {
            Add-Error "Remove smoke did not prune empty legacy directory: $legacyFull"
        }
    }
    finally {
        if (Test-Path $tmpHome) {
            Remove-Item -LiteralPath $tmpHome -Recurse -Force
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "Dreamers Copilot validation passed." -ForegroundColor Green
