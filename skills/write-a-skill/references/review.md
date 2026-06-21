# Review

Quality checklist + failure-mode diagnostics. Run after the structural validator
passes and after every iteration. Read the body as if you are an agent
encountering the skill for the first time.

## Table of contents

1. [Quality checklist](#quality-checklist)
2. [Failure modes](#failure-modes)
3. [Pruning pass](#pruning-pass)
4. [Trigger pass](#trigger-pass)

## Quality checklist

### Frontmatter

- [ ] `name` matches the directory name exactly.
- [ ] `name` is kebab-case, 1–64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`.
- [ ] `description` is 1–1024 chars, single line, no YAML `>` or `|`.
- [ ] `description` opens with the skill's leading word.
- [ ] No XML angle brackets `<` `>` in the description.
- [ ] No `claude` or `anthropic` in `name`.
- [ ] No `README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md` in the folder.

### Description (tier 1)

- [ ] First sentence says what the skill does.
- [ ] Lists verbatim trigger phrases the user actually says.
- [ ] Lists relevant file types if format-bound.
- [ ] Includes ≥1 negative trigger if a near-miss skill exists.
- [ ] One trigger per distinct branch — synonyms collapsed.
- [ ] No identity that is already in the body (the body can restate triggers for
      the activated agent; the description should not repeat body content).

### Body (tier 2)

- [ ] Under 500 lines. If over, disclose to a reference.
- [ ] Imperative form throughout.
- [ ] Explains *why* over rigid MUST/NEVER (yellow flag if you see them in
      caps).
- [ ] 2–3 concrete input/output examples — not vague.
- [ ] Critical instructions at the top, not buried mid-body.
- [ ] Every reference / script linked with a one-line load condition
      ("read when…", "run when…").
- [ ] No line wraps at arbitrary column widths inside prose paragraphs — each
      sentence or paragraph is a single long line (some renderers treat hard
      breaks as visual breaks). Code blocks are exempt.

### Steps (when the skill has them)

- [ ] Every step ends on a **completion criterion** — a checkable condition
      that tells the agent the step is done.
- [ ] Strongest criteria are both *checkable* (agent can tell done from
      not-done) and *exhaustive* ("every modified model accounted for", not
      "produce a change list").
- [ ] No step whose post-completion steps tempt the agent to rush the current
      one. If you observe the rush in real use, split the sequence.

### References (tier 3)

- [ ] One level deep from SKILL.md.
- [ ] Files >300 lines have a table of contents at the top.
- [ ] Each file named for what it holds.
- [ ] No content duplicated between SKILL.md and a reference (single source of
      truth).

### Scripts

- [ ] Every script actually runs — tested before shipping.
- [ ] Has a clear contract: inputs, outputs, exit codes.
- [ ] Linked from SKILL.md with a one-line run condition.

## Failure modes

The default state of a skill under maintenance is decay. These are the levers
to diagnose when the skill misbehaves. They overlap; one symptom often has
several contributors.

### Premature completion

Ending a step before it is genuinely done, attention slipping to *being done*.

**Diagnostic.** The agent declares a step complete on weak evidence.

**Defences, in order of cost:**

1. **Sharpen the completion criterion.** Cheap, local. Replace "understanding
   reached" with "every modified model accounted for".
2. Only when the criterion is irreducibly fuzzy *and* you observe the rush,
   **hide the post-completion steps** by splitting the sequence into a separate
   skill or subagent dispatch. Hiding only works across a real context
   boundary; inline model-invoked calls leave later steps visible.

### Duplication

The same meaning in more than one place. Costs maintenance (change one place,
must change others), tokens, and inflates a meaning's prominence past its real
rank.

**Diagnostic.** Find the same idea in SKILL.md and a reference, or restated at
two sites in the body.

**Fix.** Pick the authoritative location; delete or link from the others. A
leading word is exempt — it repeats a *token*, never a meaning.

### Sediment

Stale layers that settle because adding feels safe and removing feels risky.
The default fate of any skill without a pruning discipline.

**Diagnostic.** Lines that no longer reflect current behavior or the current
shape of the task.

**Fix.** Run the [Pruning pass](#pruning-pass) every iteration.

### Sprawl

A skill simply too long, even when every line is live and unique. Hurts
readability (the agent wades before acting) and maintainability.

**Diagnostic.** SKILL.md >500 lines, or each path through the skill forces the
agent to skim material that does not apply to it.

**Fix.** Push reference down behind context pointers. Split by branch (a way
the skill is used only some of the time) or by sequence (post-completion steps
that invite rushing).

### No-op

An instruction that changes nothing because the agent already does it by
default.

**Diagnostic.** Apply the **no-op test** sentence by sentence: *does this line
change behavior versus the default?* If not — regardless of how relevant it
feels — it is a no-op. Paying load to say nothing.

**Fix.** Delete the line. Do not rewrite it shorter; the line is the problem,
not its length. A weak leading word (`be thorough` when the agent is already
thorough-ish) is also a no-op — the fix is a stronger word (`relentless`), not
a different technique.

**Note.** No-op is model-relative. Two people disagreeing about whether a line
is a no-op are disagreeing about the model's default. Settle it by running the
skill, not by debate.

## Pruning pass

Run every iteration, before adding anything new. Most iterations should make
the skill shorter.

For each line in SKILL.md (and each reference file when it is opened):

1. **Relevance** — does this line still bear on what the skill does? Either it
   never bore on the task (mere exposition, or a branch that should have been
   disclosed), or it has gone stale. Delete.
2. **No-op** — does this line change behavior versus the default? If not,
   delete.
3. **Single source of truth** — is this meaning stated anywhere else? If yes,
   delete one site; keep the authoritative one.
4. **Duplication** — are two phrasings restating one branch? Collapse to one.

Cut first, add second. If you cut a real problem, the skill gets sharper. If
you cut a load-bearing line, the next real use surfaces it and you restore with
better wording.

## Trigger pass

For each of these phrases, would the description fire correctly?

- **Should fire**: the obvious task request; a casual paraphrase; a partial /
  informal version with typos or abbreviations.
- **Should NOT fire**: an unrelated topic; a task owned by a neighbor skill; a
  generic question the agent handles unaided (skills only help for tasks the
  agent cannot easily do alone).

If a should-fire would not trigger, the description is too narrow. If a
should-not-fire would, it is too broad. Refine and re-run.

Edge case: trivial one-step queries ("read file X") may not trigger any skill
even when the description matches perfectly, because the agent handles them
directly with basic tools. This is correct behavior, not a missed trigger.
Build trigger-test phrases that are substantive enough to benefit from skill
consultation.
