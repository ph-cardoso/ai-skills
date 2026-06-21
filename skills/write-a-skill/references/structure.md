# Structure

Reference for skill anatomy, progressive disclosure, frontmatter rules, the
description as the only trigger, and degrees of freedom. Read once before
drafting any skill body.

## Table of contents

1. [Folder layout](#folder-layout)
2. [Progressive disclosure](#progressive-disclosure)
3. [Frontmatter](#frontmatter)
4. [Name rules](#name-rules)
5. [Description](#description)
6. [Degrees of freedom](#degrees-of-freedom)
7. [OpenCode specifics](#opencode-specifics)
8. [Bundled resources](#bundled-resources)
9. [What never to include](#what-never-to-include)

## Folder layout

```
skill-name/
├── SKILL.md              # required: metadata + body
├── references/           # optional: docs loaded on demand
│   └── <topic>.md
├── scripts/              # optional: deterministic, executable code
│   └── <task>.py
└── assets/               # optional: templates, fonts, icons — used in output
    └── <template>
```

One level deep only. Do not nest reference files inside other reference files;
every reference links directly from SKILL.md.

## Progressive disclosure

Three loading tiers, ranked by how immediately the agent needs the material:

| Tier | What | When loaded | Budget |
|---|---|---|---|
| 1 | frontmatter (`name` + `description`) | every turn | ~100 words |
| 2 | SKILL.md body | on trigger | <500 lines |
| 3 | `references/` `scripts/` `assets/` | as needed | unlimited |

Push material down the ladder whenever the top grows past legible. The test:
inline what every code path needs; disclose behind a pointer what only some
paths reach.

Two signals it is time to split a reference out of SKILL.md:

- The body approaches ~400–500 lines.
- A region of the body serves a *branch* — a way the skill is used only some of
  the time. Branch-specific material is the cleanest disclosure candidate.

A reference file's *name and the wording of the pointer to it* decide when (and
how reliably) the agent reaches it. Sharpen the pointer before inlining the
material.

## Frontmatter

OpenCode recognizes these fields. Unknown fields are silently ignored (see
[OpenCode specifics](#opencode-specifics)).

```yaml
---
name: <required, kebab-case, matches folder>
description: <required, 1–1024 chars, single line — no YAML multiline operators>
license: <optional, e.g. CC-BY-4.0, MIT>
compatibility: <optional, e.g. opencode>
metadata: <optional, string-to-string map>
  author: <name>
  version: <semver>
---
```

Hard rules:

- `name`: lowercase alphanumeric + single hyphens, 1–64 chars, must match the
  containing directory name.
- `description`: no YAML `>` or `|` block scalars. Write it as a single inline
  string. If you need a long description, write one long line.
- Delimiters: exactly `---` on their own lines, nothing else on those lines.
- Never include `claude` or `anthropic` in `name` — reserved.

If the YAML does not parse, OpenCode silently drops the skill. Always run
`scripts/validate_skill.py` after editing frontmatter.

## Name rules

Regex equivalent:

```
^[a-z0-9]+(-[a-z0-9]+)*$
```

- 1–64 characters
- lowercase alphanumeric only
- single hyphens as separators; no leading/trailing hyphen; no consecutive `--`
- name must equal the directory name containing SKILL.md

Naming guidance:

- Short, verb-led phrases describing the action: `git-release`, `tdd`,
  `caveman-commit`.
- Namespace by tool when it improves clarity or trigger accuracy:
  `gh-address-comments`, `linear-address-issue`.
- Normalize user-supplied titles to kebab-case: "Plan Mode" → `plan-mode`.

## Description

The description is the **only** signal at tier 1. The body is irrelevant until
the description fires. Agents undertrigger by default, so the description must
be specific and slightly pushy.

Shape:

```
[What it does] + [When to use: verbatim trigger phrases, file types, contexts]
                + [What NOT to use it for: near-misses owned by neighbor skills]
```

Principles:

- **Front-load the skill's leading word.** The first ~10 words carry the most
  weight.
- **One trigger per branch.** If two phrases rename the same branch ("build
  features with TDD" / "asks for test-first development") they are duplicates —
  collapse to one. Keep only genuinely distinct triggers.
- **Include verbatim phrases the user actually says**, not abstract
  descriptions of intent. Real prompts, with casual speech, abbreviations,
  typos.
- **List relevant file types** if the skill is format-bound (`.docx`, `.pdf`).
- **Add negative triggers** when a near-miss skill exists. "Do NOT use for X"
  prevents cross-talk.
- **No XML angle brackets** `<` `>` in the description — they break some
  renderers.

Good:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when
working with PDFs, or when the user mentions PDFs, forms, or document
extraction. Do NOT use for images or screenshots.
```

Bad:

```
Helps with documents.
```

The bad description gives the agent no way to distinguish this skill from any
other document-handling skill — it will never fire reliably.

### Description length

1–1024 chars enforced by OpenCode. Aim for 200–500: long enough to list real
triggers, short enough not to bloat tier-1 context for every skill installed.

## Degrees of freedom

Match instruction specificity to task fragility. Wrong freedom = either brittle
or hand-wavy.

| Freedom | Form | Use when |
|---|---|---|
| **High** | prose, heuristics | many valid approaches; decision depends on context |
| **Medium** | pseudocode or parameterized script | preferred pattern exists; some variation acceptable |
| **Low** | specific script, few parameters | operation is fragile, error-prone, or must be consistent every time |

Heuristic: a narrow bridge with cliffs needs guardrails (low freedom); an open
field allows many routes (high freedom). Default to high; drop freedom only
where the agent keeps getting it wrong.

## OpenCode specifics

Discovered from `https://opencode.ai/docs/skills/` — re-verify if behavior
changes.

**Discovery paths** (loaded globally + walked from cwd up to the git worktree):

- `~/.config/opencode/skills/<name>/SKILL.md`
- `~/.opencode/skills/<name>/SKILL.md` (project)
- `~/.claude/skills/<name>/SKILL.md` (global + project)
- `~/.agents/skills/<name>/SKILL.md` (global + project)

**Frontmatter**: only `name`, `description`, `license`, `compatibility`,
`metadata` are recognized. Unknown fields are ignored.

**`disable-model-invocation: true` is NOT honored by OpenCode.** It is a
Mattpocock-skill convention that some clients respect, but OpenCode will still
expose the description to the agent. If you want a user-invoked-only skill on
OpenCode, the only reliable lever is `permission.skill` in `opencode.json`:

```json
{
  "permission": { "skill": { "internal-*": "ask" } }
}
```

Permission values: `allow` (load immediately), `deny` (hidden from agent),
`ask` (prompt user). Patterns support `*` wildcards. Per-agent overrides via
agent frontmatter `permission.skill` or `opencode.json` `agent.<name>.permission.skill`.

**Tool integration**: OpenCode lists available skills in the `skill` tool
description; the agent calls `skill({ name: "..." })` to load a body.

## Bundled resources

### scripts/

Executable code (Python, Bash, etc.) for tasks needing deterministic
reliability or that would be re-derived every run.

- Include when: same logic keeps getting rewritten, or output must be exact.
- Test every script by actually running it before the skill ships. A
  representative sample is enough when there are many similar scripts.
- Scripts may still need to be read for patching or environment-specific fixes —
  do not treat them as opaque.

### references/

Documentation loaded on demand. The main lever for keeping SKILL.md lean.

- Include when: material exceeds ~100 lines or applies to only some branches.
- Avoid duplication: a piece of information lives in either SKILL.md or a
  reference file, not both. When in doubt, prefer the reference file.
- For files >300 lines, put a table of contents at the top so the agent can
  preview scope before reading.
- Name files for what they hold. Link each from SKILL.md with a one-line load
  condition ("read when…", "run when…").

### assets/

Files used in the output the agent produces, not loaded into context.

- Include when: the skill produces output that copies or modifies a template,
  font, icon, sample document.
- Examples: `assets/logo.png`, `assets/hello-world/` boilerplate,
  `assets/font.ttf`.

## What never to include

The skill folder is for an agent, not a human maintainer. Do not create:

- `README.md`
- `CHANGELOG.md`
- `INSTALLATION_GUIDE.md`
- `QUICK_REFERENCE.md`
- `CONTRIBUTING.md`
- `LICENSE` file (license goes in frontmatter `license:`)
- Anything else whose audience is "a human reading the repo"

These add clutter, confuse the agent about which file is authoritative, and
inflate the skill's footprint on disk and in any packaging step. The
`validate_skill.py` script flags them.
