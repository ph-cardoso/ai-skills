# Conventional Commits Reference

Full spec distilled from [conventionalcommits.org v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and the [Angular commit message guidelines](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines). Read when formatting any commit.

## Table of contents

1. [Format anatomy](#format-anatomy)
2. [Types](#types)
3. [Scope](#scope)
4. [Subject](#subject)
5. [Body](#body)
6. [Footer](#footer)
7. [Breaking changes](#breaking-changes)
8. [Revert](#revert)
9. [Worked examples](#worked-examples)

## Format anatomy

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

Rules:

- The header (first line) is mandatory; scope is optional.
- Body is optional; include when the "why" is not obvious from the subject.
- Footer is optional; used for breaking changes and issue references.
- No line longer than 100 characters (Angular rule). Subject target ≤72.
- Use the imperative present tense everywhere: "add" not "added" or "adds".
- Always English, regardless of the repo's working language.
- Never append `Co-Authored-by` or `Generated with` trailers.

## Types

| Type | Use for | SemVer impact |
|------|---------|---------------|
| `feat` | a new feature for the user | MINOR |
| `fix` | a bug fix | PATCH |
| `docs` | documentation only changes | none |
| `style` | formatting, whitespace, semicolons — no logic change | none |
| `refactor` | code change that neither fixes a bug nor adds a feature | none |
| `perf` | code change that improves performance | none |
| `test` | adding missing tests or correcting existing tests | none |
| `build` | changes to the build system or external dependencies | none |
| `ci` | changes to CI configuration files and scripts | none |
| `chore` | maintenance, tooling, config not covered above | none |
| `revert` | reverts a previous commit | varies |
| `merge` | merge commits | none |

Only `feat`, `fix`, and any commit with a breaking-change marker affect SemVer. The other types are organizational and have no implicit version impact.

## Scope

The scope is a free-form noun describing the affected domain, in parentheses immediately after the type:

- `feat(auth): ...`
- `fix(api): ...`
- `docs(readme): ...`
- `refactor(parser): ...`
- `chore(deps): ...`

Pick the scope from the changed domain, not from the file path. When a change spans the whole codebase or has no single home, omit the scope entirely:

- `style: apply prettier to src/`
- `test: cover edge cases across modules`
- `docs: fix typos`

## Subject

- Imperative present tense: "add OAuth2 refresh" not "added" or "adds".
- Lowercase first letter.
- No trailing dot.
- ≤72 characters (target); the 100-character hard cap covers the full header line.
- Specific: "handle token expiry at midnight boundary" beats "fix token bug".

## Body

- Imperative present tense, same as the subject.
- Explain the motivation for the change and contrast with previous behavior.
- Wrap at 100 characters.
- One blank line between subject and body.
- Use bullet lists (`-`) for multi-point explanations; they read faster than prose.
- Optional. Skip when the subject alone is clear.

## Footer

One blank line after the body (or after the subject if there is no body). Footer tokens use `-` for internal whitespace, except `BREAKING CHANGE` which keeps its space:

- `BREAKING CHANGE: <description>` — signals a breaking change (uppercase, mandatory token).
- `Closes #123`, `Fixes #456` — close issues on merge.
- `Refs #789` — related reference without closing.
- `Reviewed-by: Name` — review attribution (rarely used by agents).
- `Co-authored-by: Name <email>` — **do NOT add** per this skill's rules.

Multiple footers stack one per line.

## Breaking changes

Signal a breaking change with BOTH the marker and the footer — never just one:

1. Append `!` immediately after the type/scope, before the colon: `feat(api)!: ...` or `feat!: ...`.
2. Add a `BREAKING CHANGE:` footer with a description of what changed and how to migrate.

The subject line summarizes the change; the footer carries the migration note. Both are required because tooling reads the `!` for SemVer and humans read the footer for impact.

Example:

```
feat(api)!: replace getUser with fetchUser

The legacy getUser() returned a plain object synchronously. fetchUser()
returns a Promise so callers can await async data sources.

BREAKING CHANGE: getUser() removed. Migrate by awaiting fetchUser() and
reading .data on the resolved value.
```

Breaking changes can attach to any type, not just `feat`: `fix`, `refactor`, `perf`, etc. all qualify if the change breaks existing API.

## Revert

Use the `revert` type, copy the original commit's subject, and reference the SHA in the body:

```
revert: feat(api): add /health endpoint

This reverts commit a1b2c3d4e5f6...

The endpoint caused a memory leak under load; rolling back until a fix lands.
```

If reverting multiple commits, list each SHA in the body.

## Worked examples

### feat with scope and body

```
feat(auth): add OAuth2 token refresh

Tokens now auto-refresh 5 minutes before expiry. Previously, users had to
re-authenticate when the token expired mid-session, interrupting long-running
workflows.
```

### fix with body explaining the bug

```
fix(parser): handle empty input without crashing

The parser threw on empty strings because the tokenizer assumed at least
one token. Added an early return for empty input and a regression test.
```

### docs with no scope

```
docs: correct typo in installation guide
```

### refactor extracting a module

```
refactor(core): extract validation into its own module

Validation logic was inline in the request handler. Moved to
src/validate.js so it can be reused by the CLI and the worker.
```

### test adding coverage

```
test(auth): cover token expiry at midnight boundary
```

### chore bumping a dependency

```
chore(deps): bump eslint to 9.1.0
```

### perf as a breaking change

```
perf(index)!: precompute lookup table at startup

Trade startup time for O(1) lookups during request handling. Previous
runtime lookup was O(n) and showed up in flame graphs under load.

BREAKING CHANGE: startup now takes ~200ms longer. Services that import
this module will see a brief delay before the first request is served.
```

### style with no scope

```
style: apply prettier to src/
```

### build switching bundlers

```
build(webpack): switch to esbuild for faster builds
```

### ci adding to the matrix

```
ci: add Node 22 to the test matrix
```

### multi-paragraph body with footers

```
fix(api): prevent racing of requests

Introduce a request id and a reference to the latest request. Dismiss
incoming responses other than from the latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now that requests are deduplicated.

Closes #123
Refs #456
```

### docs with scope and issue close

```
docs(readme): document the new --dry-run flag

Closes #89
```

### revert with body and SHA

```
revert: feat(auth): add OAuth2 token refresh

This reverts commit a1b2c3d4e5f6789...

Caused a regression where short-lived sessions lost their token. Rolling
back until the refresh logic handles sub-minute sessions correctly.
```
