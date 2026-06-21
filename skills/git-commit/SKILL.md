---
name: git-commit
description: Enforces commit and push discipline for AI-assisted git work: never auto-commit or auto-push without a direct command, always ask when in doubt, split changes into one commit per feature/domain/goal, and format every commit as a Conventional Commit (Angular variant) in English. Use when the user says "commit this", "commit the changes", "push", "push these", "split into commits", or any phrase containing the literal verbs "commit" or "push". Also use proactively before staging any modified files, or whenever the agent considers writing to git history. Do NOT use for reading git state like status/diff/log, for branch operations, rebases, cherry-picks, or PR creation — those are out of scope.
license: MIT
compatibility: opencode
metadata:
  author: ph-cardoso
  version: 0.1.0
---

# Git Commit

Enforces the user's personal commit and push discipline: the agent never writes to git history without a direct command, splits changes by feature/domain/goal, and formats every commit per Conventional Commits (Angular variant) in English. The user reviews agent work through the git diff view, so the history must read as a clean, attributable log of what the agent did and why.

## When to use

Triggers (literal verbs only — paraphrases do NOT authorize action):
- "commit", "commit this", "commit the changes", "split into commits", "commit the api rewrite"
- "push", "push these", "push to origin"

Anti-triggers (do NOT fire this skill):
- "show me the diff", "what changed", "git status", "git log" → read-only inspection, no commit skill needed
- "create a branch", "rebase", "merge", "open a PR", "cherry-pick" → out of scope
- "save", "done", "wrap up", "finalize", "ship it", "we're good" → NOT commit commands; treat as ambiguous and ask the user

## Rules

### Rule 1: Never auto-commit, never auto-push

The agent MUST NOT run `git commit` or `git push` unless the user's current message contains the literal verb "commit" or "push". This is non-negotiable because commits and pushes are irreversible writes to shared history, and the user evaluates agent work by reading the diff before anything lands. Paraphrases like "save", "done", "wrap up", "finalize", or "ship it" do NOT authorize a commit — they signal the task is finished, not that history should be written. When unsure whether a phrase authorizes commit or push, stop and ask.

### Rule 2: Ask when in doubt

If any of the following are unclear, stop and ask the user before staging anything: whether to commit at all; how to split changes across multiple commits; which type or scope applies; whether a change counts as breaking; whether to push after committing; whether to include a file the agent did not touch. Asking once costs less than a wrong commit.

### Rule 3: Stage own work only

Before staging, run `git status` and inspect the diff. Stage ONLY files the agent modified during this session. If the working tree contains changes the agent did not make (user edits, other tools, pre-existing unstaged work), leave them untouched and report them in the summary. Never use `git add -A` or `git add .` blindly — they sweep up work that does not belong to the agent.

### Rule 4: Split by feature, domain, or goal

Group related changes into separate commits, one per coherent unit of work. A feature plus its tests is one commit; an unrelated refactor and an unrelated bugfix are two commits; a config tweak alongside feature work is two commits. Never bundle unrelated changes into a single commit just because they were made in the same session. If the split is unclear, propose a grouping to the user and wait for confirmation.

### Rule 5: Validate before staging

Run the repo's lint, format, and typecheck commands before staging (check `package.json`, `Makefile`, `AGENTS.md`, or project README for the right command). If any check fails, abort the commit, report the failure, and fix the issue. Never bypass pre-commit hooks with `--no-verify` — a hook failure means the commit should not land.

### Rule 6: Conventional Commits, English, no trailers

Every commit message follows the Conventional Commits spec (Angular variant), summarized below and documented in full in `references/conventional-commits.md`:

- Format: `<type>(<scope>): <subject>` on the first line, optional body after a blank line, optional footer after another blank line.
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `merge`.
- Scope: free-form noun for the affected domain, e.g. `auth`, `api`, `skills`. Omit when the change is cross-cutting.
- Subject: imperative present tense ("add" not "added"), lowercase first letter, no trailing dot, ≤72 characters.
- Body: imperative present tense, wrapped at 100 characters, included only when the "why" is not obvious from the subject.
- Breaking change: append `!` after type/scope AND add a `BREAKING CHANGE:` footer describing the impact and migration path.
- Language: always English, regardless of the repo's working language.
- Never append `Co-Authored-by` or `Generated with` trailers — the user wants commits to read as their own.

## Process

### Step 1: Confirm intent

Check the user's message for the literal verb "commit" or "push". If neither appears, do not stage anything. Ask: "Did you want me to commit these changes, or leave them unstaged for your review?"

Completion criterion: explicit commit or push authorization confirmed in the user's own words.

### Step 2: Inspect the working tree

Run `git status` and `git diff`. Classify every modified file as either "agent-touched this session" or "other" (user edits, pre-existing, other tools). Only agent-touched files are candidates for staging.

Completion criterion: every modified file labeled "agent-touched" or "other", with "other" files listed for the summary.

### Step 3: Validate

Run lint, format, and typecheck. Fix any failures. Re-run until clean.

Completion criterion: all validation commands exit 0.

### Step 4: Group changes

Cluster agent-touched files by feature, domain, or goal. For each group, decide a type, scope, and subject. If a single file straddles two groups, decide by the primary change or ask the user. If the split is ambiguous, propose the grouping and wait.

Completion criterion: a written list of groups, each with `(files) → type(scope): subject`, reviewed against the diff.

### Step 5: Stage and commit per group

For each group, in dependency order: stage the specific files with `git add <file1> <file2>`, then commit with `git commit -m "<type>(<scope>): <subject>"` (add a `-m` body only when the why is not obvious). Never use `git add -A` or `git add .`. Report each commit's short hash and subject as it lands.

Completion criterion: every group committed; `git status` shows only "other" files remaining.

### Step 6: Push only on explicit command

If the user's message contained "push", run `git push` (or `git push origin <branch>` if a branch is specified). If the user said only "commit", stop after step 5 and wait — do not infer a push. If unsure whether to push, ask.

Completion criterion: push executed only when the user's message contained the literal verb "push".

## Examples

### Example 1: Single clean commit

User says: "commit this fix"
Changes: `src/auth.py` (bug fix in token expiry edge case), agent-touched.
Actions:
1. `git status` → only `src/auth.py` modified by agent.
2. Run `pytest` → passes.
3. Group: `src/auth.py` → `fix(auth): handle token expiry at midnight boundary`.
4. `git add src/auth.py && git commit -m "fix(auth): handle token expiry at midnight boundary"`.
Result: one commit `a1b2c3d`, clean tree, no push (user said "commit", not "push").

### Example 2: Split into multiple commits

User says: "commit these"
Changes: `src/api.py` (new endpoint), `src/api_test.py` (its tests), `README.md` (unrelated typo fix), all agent-touched.
Actions:
1. `git status` → three files modified by agent.
2. Run `pytest` and `ruff` → both pass.
3. Group A: `src/api.py` + `src/api_test.py` → `feat(api): add /health endpoint`.
4. Group B: `README.md` → `docs: fix typo in installation section`.
5. Stage + commit A, then stage + commit B.
Result: two commits, each a coherent unit; no push.

### Example 3: Ambiguous authorization — ask, do not act

User says: "ok we're done here"
Actions:
1. Detect: no literal "commit" or "push" verb in the message.
2. Do NOT stage or commit anything.
3. Ask: "Done — did you want me to commit the changes, or leave them unstaged for your review?"
Result: no git action until the user replies with an explicit verb.

### Example 4: Breaking change with both signals

User says: "commit the api rewrite"
Changes: removes the public `getUser()` method, replaces with `fetchUser()`.
Actions:
1. Detect breaking change (removed public API).
2. Compose the message with `!` marker and `BREAKING CHANGE:` footer:

```
feat(api)!: replace getUser with fetchUser

The legacy getUser() returned a plain object synchronously. fetchUser()
returns a Promise so callers can await async data sources.

BREAKING CHANGE: getUser() removed. Migrate by awaiting fetchUser() and
reading .data on the resolved value.
```

3. `git add src/api.ts && git commit -F <message-file>` (or `-m` with heredoc).
Result: one commit with both breaking-change signals per the spec.

### Example 5: Mixed working tree — own work only

User says: "commit my changes"
Working tree: `src/parser.py` (agent-touched), `notes.md` (user's own scratch file, unstaged before the session).
Actions:
1. `git status` → both files modified.
2. Classify: `src/parser.py` = agent-touched; `notes.md` = other (not touched this session).
3. Stage only `src/parser.py`. Commit as `fix(parser): handle empty input`.
4. Report: "Committed `src/parser.py` as `b3c4d5e`. Left `notes.md` unstaged — it looks like your own work."
Result: agent's commit does not sweep up the user's unrelated file.

## References

- `references/conventional-commits.md` — read when formatting any commit. Full spec distilled from conventionalcommits.org v1.0.0 and the Angular CONTRIBUTING guidelines: format anatomy, the 12 allowed types with SemVer impact, scope guidance, subject/body/footer rules, breaking-change patterns, revert convention, and 12 worked examples covering every type.
