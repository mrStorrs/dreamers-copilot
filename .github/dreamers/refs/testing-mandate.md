## Plan template
Plans use Goal and Acceptance criteria, matching GitHub issue proposals. Choose appropriate test layers from the observable outcomes; layer annotations are not required in plans.

## Coverage requirement (every plan)

Implementation tests must cover the following whenever applicable to the work:

**Unit layer**
- Each significant function, method, or class in isolation.
- All branches: happy path, edge cases (boundary values, empty/null/max), negative cases (invalid input, error states).
- Any pure logic that does not require a real device, network, or database.

**Integration layer**
- Interactions between layers: repository ↔ data source, ViewModel ↔ repository, service ↔ external API.
- Database reads/writes (real or in-memory, not mocked).
- Auth flows end-to-end within the backend.
- Cloud function triggers and side-effects.

**UI / E2E layer**
- Full user journeys through the UI: screen load → interaction → outcome visible on screen.
- Navigation flows between screens.
- Error and empty states rendered correctly in the UI.
- Any flow that requires a real device or emulator.
- **Navigation change rule (mandatory):** When a plan changes how a nav element behaves (tab tap, modal open, screen transition), verify the changed navigation through E2E coverage. Probe checks this in the layer audit.

If a layer cannot be covered automatically (e.g., camera permission flows), put the manual steps, expected result, and reason under the relevant AC; set `User-testing-required: yes`.

## Test benchmarks

Keep `./test-benchmarks.md` at the project root and commit it to version control.

- If the file is absent, create it after the first successful test run. Include only a Markdown table with `Command`, `Last Run`, and `Recommended Timeout`, in that order. Use the template below.
- For each successful run, add or update the row for its command. Record the latest successful duration in `Last Run` and set `Recommended Timeout` to `max(2 × last run, 30s)`. Use an existing command's recommended timeout when preparing to run it.
- If the existing table has extra columns, ask the user before backfilling it. If approved, keep every command row and its recorded duration and timeout, map the duration column to `Last Run`, and remove the extra columns and explanatory prose. If declined, keep the existing layout and continue updating its timing fields after successful runs.
- Template: `.github/dreamers/templates/test-benchmarks.md` (catalog-relative; resolves to `~/.copilot/dreamers/templates/test-benchmarks.md` at install).
