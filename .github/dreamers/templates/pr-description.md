# PR description

<pr-description>

Use this structure for the PR body. Omit untouched platforms and the fixes section when no fixes apply.

```markdown
## Summary
plan/task summary here

- [bullet: what was delivered]
- [bullet: why / what problem it solves]

## Test counts

- Desktop Vitest: N pass
- Mobile Jest: N pass

*(Omit platforms not touched by this PR.)*

## Fixes applied

- [SEVERITY] file:line — what was fixed (from reviewer artifacts / commit messages)

*(Omit if no fixes applied.)*
```

</pr-description>
