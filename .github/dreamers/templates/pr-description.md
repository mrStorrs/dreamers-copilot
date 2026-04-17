# PR Description Template

Use this structure for `gh pr create --body`.

---

## Summary

- [bullet: what was delivered]
- [bullet: why / what problem it solves]

## Files changed

| File | Change |
|---|---|
| `path/to/file.ts` | [one-line reason] |

## Test counts

- Desktop Vitest: N pass
- Mobile Jest: N pass

*(Omit platforms not touched by this PR.)*

## Sentinel findings resolved

- F-N (severity): [one-line description of what was fixed]

*(Omit if no findings.)*

## Firebase build

Release X.Y.Z (build N) distributed to alpha group — available in Firebase App Tester.

*(Replace with "N/A — no mobile runtime changes" if skipped.)*

---

🤖 Generated with GitHub Copilot
