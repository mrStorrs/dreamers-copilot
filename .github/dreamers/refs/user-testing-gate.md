# User Testing Gate Template

Use this template whenever the Dreamers pipeline pauses for user testing.

Call `request_information`. Do not replace this gate with an unstructured chat prompt unless the tool is unavailable.

## Prompt body

The prompt body must contain exactly these two sections, in this order:

### Testing steps

Number every required user action and verification step with `1.`, `2.`, `3.`.

Include:
- Plan ID + path.
- A one-sentence summary of what changed in this cycle.
- Every special action required before testing, including build type, packaging, deploy, install, cache reset, seed data, feature flag, account state, device/browser, or distribution steps.
- Build/distribute steps from `.github/instructions/build.instructions.md` when present.
- If `.github/instructions/build.instructions.md` is absent and a build/distribution action is needed, include a numbered step asking the user to perform the project-specific build/distribution manually.
- Every manual test the user should perform, derived from the plan ACs and any reviewer-requested validation.
- The expected result for each test step.

Do not collapse tests into a paragraph. Do not use bullets for the testing steps.

### Notes

Include:
- Known limitations and out-of-scope items.
- Relevant automated validation already run.
- Any environment assumptions or risks the user should know before approving.

Use `None` only when there are no notes.

## Options

Provide exactly these three options:

1. `Approved`
2. `Bug found (enter text)`
3. `Other (enter text)`

`Bug found (enter text)` and `Other (enter text)` must accept freeform text.

## Response handling

- `Approved` -> continue the pipeline.
- `Bug found (enter text)` -> capture the bug text, fix inline, rerun required automated validation, then present this same user-testing gate again.
- `Other (enter text)` -> follow the user's direction. If the result still needs user testing sign-off, present this same gate again.
