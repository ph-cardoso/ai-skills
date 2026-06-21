#!/usr/bin/env python3
"""Structural validator for an Agent Skills skill folder.

Run:
    python3 scripts/validate_skill.py <path-to-skill-folder>

Exits 0 if clean, 1 if any check fails. Checks:

  - SKILL.md exists, exact casing
  - YAML frontmatter parses
  - required fields present (name, description)
  - name matches regex ^[a-z0-9]+(-[a-z0-9]+)*$ and equals folder name
  - description length 1-1024 chars
  - description has no YAML multiline operators (> or |) as the value's first
    non-space char on the same line as the key
  - description has no XML angle brackets < >
  - no forbidden auxiliary docs (README, CHANGELOG, INSTALLATION_GUIDE, etc.)
  - reference files under references/ over 300 lines have a table of contents
  - frontmatter uses only recognized OpenCode fields (warn, not fail)

Single-file, stdlib only.
"""

import re
import sys
from pathlib import Path

NAME_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DESCRIPTION_MAX = 1024
REFERENCE_TOC_THRESHOLD_LINES = 300
FORBIDDEN_FILES = {
    "readme.md",
    "changelog.md",
    "installation_guide.md",
    "quick_reference.md",
    "contributing.md",
    "license",
    "license.md",
}
RECOGNIZED_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata"}


def parse_frontmatter(text):
    """Return (frontmatter_str, body_str) or (None, text) if no frontmatter.

    Minimal YAML-ish fence parser. Does not evaluate the YAML; the caller
    validates the field block separately.
    """
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None, text
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    return fm, body


def parse_yaml_block(fm_str):
    """Tiny YAML parser for flat key: value pairs and one nested map (metadata).

    Returns dict of {key: value_or_dict}. Values are strings (possibly
    multi-line for block scalars > or |). Sufficient for validation; not a
    general YAML parser.
    """
    result = {}
    lines = fm_str.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        stripped = line.strip()
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", stripped)
        if not m:
            i += 1
            continue
        key, value = m.group(1), m.group(2)
        if value == "":
            # nested map: collect subsequent indented lines as key: value pairs
            nested = {}
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    j += 1
                    continue
                if not (nxt[:1] in (" ", "\t")):
                    break
                nm = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", nxt)
                if nm:
                    nested[nm.group(1)] = nm.group(2)
                j += 1
            result[key] = nested
            i = j
            continue
        if value[:1] in (">", "|"):
            # block scalar: collect subsequent indented lines as the value
            collected = [value[1:].strip()]
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if not nxt.strip():
                    collected.append("")
                    j += 1
                    continue
                if not (nxt[:1] in (" ", "\t")):
                    break
                collected.append(nxt.strip())
                j += 1
            result[key] = value[:1] + " " + " ".join(collected).strip()
            i = j
            continue
        result[key] = value
        i += 1
    return result


def count_description_chars(value_str):
    """Estimate description character count from its raw value string.

    Handles quoted strings, block scalars (> or |), and bare values.
    """
    v = value_str.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return len(v[1:-1])
    if v[:1] in (">", "|"):
        # block scalar: count chars after the indicator, joining wrapped lines
        rest = v[1:].strip()
        if not rest:
            return 0
        return len(rest)
    return len(v)


def validate(skill_path):
    skill = Path(skill_path).resolve()
    errors = []
    warnings = []

    if not skill.is_dir():
        errors.append(f"not a directory: {skill}")
        return errors, warnings

    skill_md = skill / "SKILL.md"
    if not skill_md.is_file():
        errors.append("SKILL.md missing (must be exact casing, all caps)")
        return errors, warnings

    text = skill_md.read_text(encoding="utf-8")
    fm_str, body = parse_frontmatter(text)
    if fm_str is None:
        errors.append("no YAML frontmatter found (must start with '---')")
        return errors, warnings

    fm = parse_yaml_block(fm_str)

    # required fields
    if "name" not in fm:
        errors.append("frontmatter: 'name' field is required")
    if "description" not in fm:
        errors.append("frontmatter: 'description' field is required")

    # unrecognized fields (warn only)
    for key in fm:
        if key not in RECOGNIZED_FRONTMATTER:
            warnings.append(
                f"frontmatter: '{key}' is not recognized by OpenCode (will be ignored)"
            )

    # name rules
    name = fm.get("name")
    if name:
        if not NAME_REGEX.match(name):
            errors.append(
                f"name '{name}' does not match ^[a-z0-9]+(-[a-z0-9]+)*$ "
                "(lowercase alphanumeric, single hyphens, 1-64 chars)"
            )
        if name != skill.name:
            errors.append(f"name '{name}' does not match folder name '{skill.name}'")
        if "claude" in name or "anthropic" in name:
            errors.append(f"name '{name}' contains reserved word (claude/anthropic)")

    # description rules
    raw_desc = fm.get("description", "")
    if isinstance(raw_desc, dict):
        errors.append("description: malformed (parsed as map, expected string)")
    elif raw_desc:
        first_char = raw_desc.lstrip()[:1]
        if first_char in (">", "|"):
            warnings.append(
                "description: uses YAML block scalar ('>' or '|') — OpenCode may "
                "load it as a multi-line string but single-line form is recommended"
            )
        else:
            if "\n" in raw_desc.strip():
                errors.append("description: spans multiple lines — must be a single line")
        char_count = count_description_chars(raw_desc)
        if char_count < 1:
            errors.append("description: empty")
        if char_count > DESCRIPTION_MAX:
            errors.append(
                f"description: {char_count} chars exceeds {DESCRIPTION_MAX} limit"
            )
        if "<" in raw_desc or ">" in raw_desc:
            if not (raw_desc.lstrip().startswith((">", "|"))):
                errors.append(
                    "description: contains XML angle brackets (< or >) — remove them"
                )

    # forbidden auxiliary docs
    for child in skill.rglob("*"):
        if child.is_file() and child.name.lower() in FORBIDDEN_FILES:
            errors.append(
                f"forbidden file present (skills are for agents, not humans): {child.name}"
            )

    # reference ToC check
    refs_dir = skill / "references"
    if refs_dir.is_dir():
        for ref in refs_dir.glob("*.md"):
            line_count = len(ref.read_text(encoding="utf-8").splitlines())
            if line_count > REFERENCE_TOC_THRESHOLD_LINES:
                head = ref.read_text(encoding="utf-8").lower()[:2000]
                if "table of contents" not in head and "## contents" not in head:
                    errors.append(
                        f"reference '{ref.name}' is {line_count} lines (>{REFERENCE_TOC_THRESHOLD_LINES}) "
                        "and has no table of contents near the top"
                    )

    return errors, warnings


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: validate_skill.py <path-to-skill-folder>\n")
        return 2
    errors, warnings = validate(argv[1])
    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    if warnings:
        print(f"\nOK with {len(warnings)} warning(s).")
    else:
        print("\nOK — skill is structurally valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
