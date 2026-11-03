**When needed**

Do the testing yourself wherever possible: use available automated tests, builds, browser/device tools, and other authorized checks. A check being manual or user-facing does not by itself require the user. Try feasible alternatives when a tool or environment blocks verification; report the limit honestly.

Request user testing only for required verification you cannot complete, or when the user explicitly wants to test personally. A plan flag is not required: uncovered task requirements, review findings, or unavailable access/devices can trigger the gate. Otherwise continue without a testing todo or approval pause.

When needed, add or reopen the user-testing todo and use this prompt. Keep it to the remaining checks and required human judgment; explain what you already verified and why the user is needed.

Call `request_information`. Do not replace this gate with an unstructured chat prompt unless the tool is unavailable.

**Prompt body**

The prompt body must contain exactly these two sections, in this order:

**Testing steps**

Number every required user action and verification step with `1.`, `2.`, `3.`.

Include:
- Task context, or plan ID + path when a plan exists.
- A one-sentence summary of what changed in this cycle.
- Only the setup actions the user still needs to perform: build/distribution, install, account state, device/browser, or other prerequisites. Complete authorized setup yourself when possible, using `.github/instructions/build.instructions.md` or other project instructions and scripts. Missing build instructions alone are not a reason to hand off testing.
- The remaining tests the user must perform, derived from task requirements, plan ACs, or reviewer-requested validation.
- The expected result for each test step.

Do not collapse tests into a paragraph. Do not use bullets for the testing steps.

**Notes**

Include:
- Known limitations and out-of-scope items.
- Relevant automated validation already run.
- Other agent-operated checks already completed and the specific limitation requiring user testing.
- Any environment assumptions or risks the user should know before approving.

Use `None` only when there are no notes.

**Options**

Provide exactly these three options:

1. `Approved`
2. `Bug found (enter text)`
3. `Other (enter text)`

`Bug found (enter text)` and `Other (enter text)` must accept freeform text.

**Response handling**

- `Approved` -> continue the pipeline.
- `Bug found (enter text)` -> capture the bug text and return to the containing skill's implementation, test, and review loop with the current context and active cap. After it succeeds, re-evaluate the remaining user checks and present the gate again if needed.
- `Other (enter text)` -> follow the user's direction. If the result still needs user testing sign-off, present this same gate again.
