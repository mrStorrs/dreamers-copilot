# Plan Naming + Location Rules

## Directory layout (mandatory)

All plans live under `.dreamers/plans/feature-<slug>/`. Flat layouts directly under `.dreamers/plans/` are not used.

```
.dreamers/plans/
├── feature-<slug>/
│   ├── manifest.md              (optional — only when multi-plan with shared context)
│   ├── plan-01-<name>.md
│   ├── plan-02-<name>.md
│   └── plan-NN-<name>.md
├── feature-<other>/
│   └── plan-01-<name>.md        (single-plan feature: no manifest needed)
└── archive/
    └── feature-<old>/           (archived features: whole dir moves at milestone-final PR merge)
```

## Feature directory naming

- Directory name: `feature-<slug>`
- Slug rules (same as before):
  - lowercase
  - replace non-alphanumerics with single hyphen
  - trim leading/trailing hyphens
  - collapse repeated hyphens
  - if empty, use `misc`

Examples:
- `feature-auth` (authentication overhaul)
- `feature-plan-format-overhaul` (the work currently in flight)
- `feature-checkout-flow` (e-commerce checkout)

## Plan filename naming

- Filename: `plan-NN-<name>.md`
  - `NN` is zero-padded two-digit order within the feature directory: `01`, `02`, ..., `99`.
  - `<name>` is a slug describing the plan's specific scope (NOT the whole feature).
- Numbered ordering reasons:
  - Survives insertion (`plan-01.5-foo` is uglier than splitting into a new feature, but at least parseable).
  - Lexically sortable when zero-padded.
  - BMad-precedented; no 26-letter cap like `-a` / `-b` / `-c`.

Examples:
- `feature-auth/plan-01-login-flow.md`
- `feature-auth/plan-02-logout.md`
- `feature-auth/plan-03-password-reset.md`
- `feature-plan-format-overhaul/plan-01-refs-and-templates.md`

Do not use lettered conventions (`plan-a-...`, `plan-b-...`) — numbered ordering is the only naming pattern.

## Manifest naming

- Path: `feature-<slug>/manifest.md`
- The manifest is OPTIONAL. Produce one only when multiple plans in the feature share cross-plan context (constraints, design decisions, data models, end-to-end ACs). See `feature-decomposition.md` for the trigger rules.

Manifests live inside the feature directory (`feature-<slug>/manifest.md`), not at the plans/ root.

## Manifest backfill (mandatory rule)

A feature directory starts with a single plan and no manifest. When a SECOND plan is added to the same feature (because the work grew beyond one plan's scope), the manifest is created at that moment.

- **Trigger:** `/dreamers-plan` Phase 1d.1 detects the feature dir already exists with `plan-01-*.md` and no `manifest.md`, AND the current planning conversation is producing what will become `plan-02-*.md` for the same feature.
- **Responsibility:** `/dreamers-plan` creates `manifest.md` during the same planning conversation that produces plan-02. Uses the existing plan-01 as the seed context.
- **Timing:** before any implementation of plan-02 starts.

## Archive rules

When a feature's plans are all shipped (single-plan: that plan; multi-plan: all plans merged), the WHOLE feature directory moves to `.dreamers/plans/archive/`:

```
.dreamers/plans/feature-auth/  →  .dreamers/plans/archive/feature-auth/
```

Never file-by-file mid-feature. Mid-feature archive would leave partially-emptied directories.

Trigger: `/dreamers-close-out` Step 7 archives the feature directory at the milestone-final PR merge — i.e., the last plan in the feature has merged to main.

## Backward compatibility

None. The new format applies to all plans written from the moment this convention ships. Existing flat plans in `.dreamers/plans/` (e.g., `plan-tdd-rewrite-a.md`) remain where they are; they are not auto-migrated. If you need to edit one, you may either rewrite it into the new format manually or leave it as legacy.
