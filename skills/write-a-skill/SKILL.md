---
name: write-a-skill
description: Design, write, evaluate, and evolve agent skills that work with OpenCode and any Agent-Skills-compatible client. Walks the full lifecycle — discovery interview, architecture, drafting, structural validation, trigger testing, qualitative review, and iteration from real use. Use whenever the user says "create a skill", "write a skill", "build a SKILL.md", "turn this into a skill", "turn this workflow into a skill", "improve this skill", "review my skill", "test this skill", "why isn't my skill triggering", mentions skill frontmatter, progressive disclosure, skill anatomy, or wants to package domain knowledge, a repeatable workflow, or a multi-step procedure into a reusable skill folder. Also use proactively when the user pastes a draft SKILL.md or describes a workflow they keep re-explaining to the agent. Do NOT use for editing opencode's own configuration (opencode.json, .opencode/) — that is config work, use the customize-opencode skill instead.
license: MIT
compatibility: opencode
metadata:
  author: ph-cardoso
  version: 1.0.0
---

# Writing Skills

A skill exists to wrangle **predictability** out of a stochastic system — the same
*process* every run, not the same output. Every decision below serves that goal:
token economy, trigger accuracy, single source of truth, and a body the agent can
follow without ambiguity.

Skills are written for an agent, not a human. No README, no CHANGELOG, no
INSTALLATION_GUIDE inside the skill folder. The reader is an LLM that loads the
description every turn and the body only on trigger.

## Process

Work the four phases in order. Each has exit criteria. Do not skip Discovery — a
skill that triggers wrong is worse than no skill.

### Phase 1 — Discovery

Goal: a mental model of the outcome, the triggers, and what "done" looks like.

Ask conversationally (one area at a time, not a checklist dump):

- **Outcome**: what workflow should become consistent? Get one concrete example,
  end to end.
- **Pain**: what goes wrong without the skill? (forgotten steps, re-explaining,
  inconsistent output, wrong triggers)
- **Audience**: just the user? a team? public? Affects naming, description
  specificity, and how hard to push the description.
- **Tools**: built-in agent tools only, or MCP / external services?
- **Triggers**: 2–3 real phrases the user would actually type. Write them down
  verbatim — they seed the description.
- **Anti-triggers**: 1–2 near-miss phrases that share keywords but should NOT
  fire this skill. These sharpen the description and prevent cross-talk with
  neighbor skills.

If the conversation already contains a workflow ("turn this into a skill"),
extract from history first, then fill gaps. If the user's need is better served
by a system prompt or project rule, say so — not everything needs to be a skill.

**Exit criteria:** ≥2 use cases captured with trigger + steps + expected result;
audience known; anti-triggers listed.

### Phase 2 — Craft

Goal: write the skill folder. Read `references/structure.md` in full before
drafting — it covers folder layout, progressive disclosure, the description as
the only trigger, degrees of freedom, and OpenCode-specific constraints.

Decide, in this order:

1. **Folder structure** — what must be deterministic → `scripts/`; what is
   reference >~100 lines → `references/`; what is template/static output →
   `assets/`; everything else stays in SKILL.md. One-level-deep references only.
2. **Description** — `[What it does] + [When to use, with the verbatim trigger
   phrases from Discovery] + [What NOT to use it for]`. Single line, no YAML
   multiline operators. See `references/structure.md#description`.
3. **Body** — imperative form. Explain *why* over rigid MUSTs. 2–3 concrete
   input/output examples. Critical instructions at the top. Reference files
   named for what they hold, with a one-line condition for *when* the agent
   should read each.
4. **Bundled resources** — scripts tested by actually running them; reference
   files >300 lines get a table of contents at the top.

Use the inline **Template** below as the starting skeleton. Information that
could live in either SKILL.md or a reference file goes to the reference file —
SKILL.md stays lean.

**Exit criteria:** folder laid out; frontmatter passes the hard rules in
`references/structure.md#frontmatter`; body under 500 lines; every referenced
file exists and has a load condition.

### Phase 3 — Validate

Goal: catch structural and trigger issues before the skill ships.

1. **Structural** — run the validator from the skill directory:

   ```sh
   python3 scripts/validate_skill.py <path-to-skill>
   ```

   It checks: SKILL.md casing, frontmatter required fields, name regex
   `^[a-z0-9]+(-[a-z0-9]+)*$`, name matches folder, description length 1–1024,
   no README/CHANGELOG/INSTALLATION_GUIDE inside the folder, table of contents
   on reference files >300 lines. Fix every reported issue before proceeding.

2. **Trigger test** — mentally walk the description against 3–5 phrases:
   - Should fire: obvious task request, a paraphrase, an informal/partial
     version.
   - Should NOT fire: unrelated topic, a task owned by a neighbor skill, a
     generic question the agent handles unaided.
   - If a should-fire phrase would not trigger, the description is too narrow;
     if a should-not-fire phrase would, it is too broad. Refine and re-test.

3. **Read-through** — read the body as if you are an agent encountering it for
   the first time. Can you follow every step? Are decision points unambiguous?
   Would you know when to stop? Then run the quality + failure-mode pass in
   `references/review.md`.

**Exit criteria:** validator clean; trigger tests pass; review checklist clean;
user confirms quality.

### Phase 4 — Iterate

Goal: evolve the skill from real use. Skills rot without a pruning discipline —
the default fate is **sediment** (stale layers settle because adding feels safe
and removing feels risky).

After each real use:

1. Note what the agent struggled with or skipped.
2. Re-read the body with `references/review.md` open — run the **no-op test**
   sentence by sentence (does this line change behavior versus the default?), the
   **relevance** check (does this line still bear on the task?), and the
   **single-source-of-truth** check (is this meaning stated anywhere else?).
3. Cut first, add second. Most iterations should make the skill shorter.
4. Re-run `validate_skill.py` after every edit.

For rigorous quantitative evaluation — parallel with-skill vs baseline runs,
assertions, pass-rate benchmarks — see `references/eval-loop.md`. Use it when
the skill is high-stakes, widely reused, or you and the user disagree about
whether a change is an improvement.

## Anatomy

A skill is a folder with a required `SKILL.md` and optional bundled resources.
OpenCode loads it through three-level **progressive disclosure**:

| Level | What loads | When | Budget |
|---|---|---|---|
| 1 — Frontmatter | `name` + `description` | every turn | ~100 words |
| 2 — Body | SKILL.md instructions | on trigger | <500 lines |
| 3 — Bundled | `scripts/` `references/` `assets/` | as needed | unlimited |

Full layout, OpenCode's recognized frontmatter fields, discovery paths, name
rules, the description as the only trigger, and degrees of freedom (when to use
prose vs pseudocode vs a deterministic script):
**read `references/structure.md` before drafting.**

## Description

The description is the **only** signal the agent sees when deciding whether to
load the skill. The body is irrelevant until the description fires. A skill
that triggers wrong is a skill that does not exist.

One line, no YAML `>` or `|`, under 1024 chars, in this shape:

```
[What it does] + [When to use, with verbatim trigger phrases and file types]
                + [What NOT to use it for]
```

Lean slightly **pushy** — agents tend to undertrigger. Better to load and not
need it than to miss a relevant query. Full guidance and good/bad examples:
`references/structure.md#description`.

## Template

Start from this skeleton. Replace `<>` placeholders. Delete sections that do
not apply. Keep the body under 500 lines — disclose to a reference file before
the top grows past legible.

```markdown
---
name: <kebab-case-name-matching-folder>
description: >
  <What it does.> Use when the user says "<verbatim trigger phrase>",
  "<another trigger>", or wants <outcome>. Also use when <adjacent context>.
  Do NOT use for <near-miss owned by another skill>.
license: <CC-BY-4.0 | MIT | >
compatibility: opencode
metadata:
  author: <author>
  version: <0.1.0>
---

# <Skill Name>

One-sentence purpose statement: what predictability this skill enforces.

## When to use

<Restate triggers here for the agent reading on activation — not for discovery,
which the frontmatter already handles.>

## Process

### Step 1: <action>

Specific, imperative instructions.

Completion criterion: <a checkable, ideally exhaustive condition that tells the
agent this step is done. "Every modified model accounted for", not "produce a
change list".>

### Step 2: <action>

...

## Examples

### Example 1: <common scenario>

User says: "<real prompt>"
Actions:
1. <step>
2. <step>
Result: <specific output>

## References

- `references/<file>.md` — read when <condition>.
- `scripts/<file>.py` — run when <condition>.
```

## Validate

Run from anywhere, pointing at the skill folder:

```sh
python3 scripts/validate_skill.py <path-to-skill>
```

Then open `references/review.md` and run the quality + failure-mode checklist.
Both must be clean before delivery.

## Iterate

Real-use loop, every time:

1. Use the skill on a real task.
2. Note struggles, skips, over-rigid moments.
3. Re-read with `references/review.md` — apply no-op, relevance, duplication,
   sediment, sprawl, and premature-completion diagnostics.
4. Cut first, add second. Re-run the validator.
5. For quantitative rigor (parallel baselines, assertions, benchmarks), open
   `references/eval-loop.md`.
