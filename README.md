# AI Skills

Personal collection of skills developed for use with AI coding agents. Each skill enforces a predictable process for a specific workflow — same steps every run, not same output.

## Skills

| Skill | Description |
|-------|-------------|
| [git-commit](skills/git-commit/) | Enforces commit/push discipline: never auto-commit, split by feature, Conventional Commits (Angular), English only. |
| [write-a-skill](skills/write-a-skill/) | Full lifecycle for designing, writing, validating, and iterating agent skills — discovery, craft, validate, iterate. |

## Compatibility

Built for [OpenCode](https://opencode.ai) and any agent client that supports the [Agent Skills](https://github.com/anthropics/agent-skills) format.

## Structure

```
skills/
  <skill-name>/
    SKILL.md          # required — frontmatter + instructions
    references/       # optional — long-form docs loaded on demand
    scripts/          # optional — deterministic helpers
    assets/           # optional — templates, static output
```

## License

MIT — see [LICENSE](LICENSE).
