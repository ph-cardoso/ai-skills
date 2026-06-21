# Eval loop

Optional, rigorous, quantitative evaluation. Use when the skill is high-stakes,
widely reused, or you and the user disagree about whether a change is an
improvement. For everyday iteration, the qualitative loop in SKILL.md's
`Iterate` section is enough.

This is an OpenCode adaptation of Anthropic's skill-creator eval workflow.
OpenCode has the `Task` tool for spawning subagents, so parallel with-skill vs
baseline runs work natively. What it does not have is a packaged HTML viewer or
a `claude -p` description-optimization loop — so the workflow below uses plain
JSON files and inline presentation instead.

## Table of contents

1. [When to use this](#when-to-use-this)
2. [Setup](#setup)
3. [Run one iteration](#run-one-iteration)
4. [Grade](#grade)
5. [Aggregate](#aggregate)
6. [Decide and iterate](#decide-and-iterate)
7. [Trigger eval (description optimization)](#trigger-eval-description-optimization)

## When to use this

Default to the qualitative loop. Escalate to this eval loop when:

- The skill is high-stakes (security, data integrity, money).
- The skill is widely reused across projects or by other people.
- A change's effect is contested — "is the new version actually better?" — and
  you want data, not vibes.
- The skill's outputs are objectively verifiable (file transforms, data
  extraction, codegen against a spec). Subjective-output skills (writing
  style, design) are better evaluated qualitatively.

## Setup

Create a workspace as a sibling of the skill directory:

```
<parent>/
├── <skill-name>/                  # the skill under test
└── <skill-name>-workspace/        # eval workspace
    └── iteration-1/
        ├── evals.json             # the test cases (shared across iterations)
        ├── <eval-name>/
        │   ├── with_skill/outputs/
        │   ├── baseline/outputs/
        │   ├── grading.json
        │   └── timing.json
        └── benchmark.json         # aggregated metrics
```

Write `evals.json` first — 2–5 realistic test prompts. The kind of thing a real
user would actually say, with file paths, casual speech, typos. Not abstract
requests.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 0,
      "name": "descriptive-kebab-name",
      "prompt": "the user's task prompt, verbatim",
      "expected_output": "what a correct result looks like",
      "files": []
    }
  ]
}
```

Assertions come later — draft them while the first runs are in flight.

## Run one iteration

For each eval, spawn two subagents **in the same turn** — one with the skill,
one without. Launching them together means they finish together; do not run
all with-skill first and come back for baselines.

**With-skill subagent prompt:**

```
Execute this task:
- Skill path: <absolute path to the skill folder>
- Task: <eval prompt>
- Input files: <eval files, or "none">
- Save outputs to: <workspace>/iteration-<N>/<eval-name>/with_skill/outputs/
- Save: <what the user cares about — e.g. "the .docx file", "the final CSV">
```

**Baseline subagent prompt** (same task, no skill path):

- For a new skill: no skill at all. Save to `baseline/outputs/`.
- For improving an existing skill: snapshot the skill first
  (`cp -r <skill> <workspace>/skill-snapshot/`) and point the baseline at the
  snapshot. Save to `old_skill/outputs/`.

If `Task` is not available (Claude.ai-style environment, no subagents), run
each with-skill case inline, one at a time, reading SKILL.md and following it.
Skip baselines — they are not meaningful without independent execution.

### Draft assertions while runs are in flight

For each eval, write objectively verifiable assertions. Good assertions:

- have descriptive names that read clearly in the benchmark viewer;
- check something the agent can verify programmatically where possible;
- are not forced onto subjective outputs (writing style, design quality).

Write a small Python script per assertion class rather than eyeballing —
faster, more reliable, reusable across iterations.

Update `evals.json` with the assertions and create a per-eval
`eval_metadata.json`:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name",
  "prompt": "the user's task prompt",
  "assertions": [
    { "text": "output file exists at <path>" },
    { "text": "every row in the CSV has a non-empty profit_margin column" }
  ]
}
```

### Capture timing

When each `Task` call completes, you receive a notification with
`total_tokens` and `duration_ms`. Save it immediately to the run's
`timing.json` — this is the only chance to capture it:

```json
{ "total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3 }
```

## Grade

Once all runs complete:

1. **Grade each run.** Either spawn a grader subagent or grade inline. For each
   assertion against each run's outputs, record `passed: bool` and `evidence`
   (a short quote or path proving the verdict). Save to `grading.json` in each
   run directory:

   ```json
   {
     "eval_name": "descriptive-name",
     "config": "with_skill",
     "expectations": [
       { "text": "output file exists", "passed": true, "evidence": "outputs/result.docx present" },
       { "text": "profit_margin non-empty", "passed": false, "evidence": "row 14 empty" }
     ]
   }
   ```

   Field names `text` / `passed` / `evidence` are fixed — the aggregator and
   any future viewer depend on them.

2. **Programmatic checks.** For assertions that can be checked by script (file
   exists, schema validates, regex matches), write and run a script. Scripts
   beat eyeballing.

## Aggregate

Compute per-config pass rate, token usage, duration, with mean ± stddev and the
delta between with-skill and baseline. Save to `iteration-N/benchmark.json`:

```json
{
  "skill_name": "example-skill",
  "iteration": 1,
  "configs": {
    "with_skill":    { "pass_rate": 0.83, "tokens_mean": 84512, "tokens_stddev": 4221, "duration_mean_s": 23.1, "duration_stddev_s": 3.4 },
    "baseline":      { "pass_rate": 0.50, "tokens_mean": 78311, "tokens_stddev": 5102, "duration_mean_s": 19.8, "duration_stddev_s": 4.1 }
  },
  "delta":          { "pass_rate": 0.33, "tokens_mean": 6201,  "duration_mean_s": 3.3 },
  "per_eval": [
    { "eval_name": "descriptive-name", "with_skill_pass_rate": 1.0, "baseline_pass_rate": 0.5 }
  ]
}
```

Then do an **analyst pass** over the benchmark:

- **Non-discriminating assertions** — pass in both configs regardless of skill.
  Drop or strengthen them.
- **High-variance evals** — large stddev, possibly flaky. Investigate.
- **Token/time tradeoff** — if with-skill costs 30% more tokens for a 5% pass
  rate gain, name the tradeoff explicitly to the user.
- **Per-eval outliers** — one eval where with-skill underperforms baseline is
  the most interesting signal in the run.

## Decide and iterate

Present results inline (no packaged viewer in OpenCode). For each eval, show
prompt, outputs side by side, formal grades. Ask the user:

1. Where does with-skill lose to baseline, or barely win? Those are the skill's
   weak spots.
2. Where does with-skill win on pass rate but the user dislikes the output?
   The assertions do not capture what the user actually values — refine them
   for the next iteration.

Apply improvements to the skill. Re-run all evals into `iteration-<N+1>/`,
including baselines. Compare against the previous iteration. Stop when:

- the user is satisfied;
- pass rates plateau;
- the cost (tokens, time) exceeds the marginal quality gain.

Generalize from feedback. The skill must work across many prompts, not
overfit to the test set. Avoid fiddly patches that fix one eval and a generic
prompt alike; prefer reframings that change how the agent thinks about the
task.

## Trigger eval (description optimization)

Separate from output quality: is the description firing on the right prompts?
Optimize it after the body is stable.

### Step 1 — Generate 20 trigger queries

A mix of should-trigger (8–10) and should-not-trigger (8–10). Realistic, with
context. Bad: `"Format this data"`. Good: `"ok so my boss just sent me this
xlsx file (its in my downloads, called something like 'Q4 sales final FINAL
v2.xlsx') and she wants me to add a column that shows the profit margin as a
percentage. revenue in column C, costs in D i think"`.

For should-not-trigger, the most valuable cases are **near-misses** — queries
that share keywords or concepts with the skill but actually need something
different. `"Write a fibonacci function"` as a negative for a PDF skill is too
easy and tests nothing.

### Step 2 — Review the set with the user

Show the queries; let the user edit, toggle, add, remove. Bad queries produce
bad descriptions.

### Step 3 — Run the optimization loop

For each query, mentally (or by spawning a subagent) check whether the agent
would load the skill. Score: should-trigger queries should fire, should-not
should not. Iterate on the description until scores stabilize:

- too narrow → add trigger phrases from real prompts the user wrote;
- too broad → add negative triggers, or move a branch to its own skill;
- both poor → the description's leading word may be wrong; pick a word the user
  actually uses when they want the skill.

This is manual in OpenCode (no `claude -p` loop). Cap at 3–5 iterations — past
that, the description is good enough and further tuning overfits.

### Step 4 — Apply

Update the SKILL.md frontmatter. Re-run the validator. Show the user the
before/after description and the trigger scores.
