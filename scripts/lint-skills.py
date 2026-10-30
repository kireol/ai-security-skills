#!/usr/bin/env python3
"""Check every skill's structure against the template. Exit 1 on any problem.

Usage: scripts/lint-skills.py
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ["SKILL.md", "incident-response.md", "references.md"]
SECTIONS = ["How to use this skill", "Deployment variants", "Discover", "Recommend", "Remediate", "Respond",
            "Version history"]
PRODUCT_SECTIONS = ["Detection"]
# Orchestration skills (skills/orchestration/) run other skills in phases, so they need fewer parts.
ORCHESTRATION_PARTS = ["SKILL.md"]
ORCHESTRATION_SECTIONS = ["How to use this skill", "Recommend", "Remediate", "Respond", "Version history"]
PREFIX = re.compile(r"^[A-Z][A-Z0-9]{0,9}$")
LINK = re.compile(r"\[[^\]]+\]\((?!https?:)([^)#\s]+)\)")

# Reuse the frontmatter parser from build-dist.py so both tools agree.
spec = importlib.util.spec_from_file_location("build_dist", ROOT / "scripts" / "build-dist.py")
build_dist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_dist)


def lint(src, prefixes):
    problems = []
    orchestration = src.parent.name == "orchestration"
    parts = ORCHESTRATION_PARTS if orchestration else PARTS
    for part in parts:
        if not (src / part).exists():
            problems.append(f"missing {part}")
    if not (src / "SKILL.md").exists():
        return problems
    text = (src / "SKILL.md").read_text()
    try:
        fm = build_dist.frontmatter(text)
    except ValueError:
        return problems + ["no frontmatter"]
    meta = fm.get("metadata", {})
    if fm.get("name") != src.name:
        problems.append(f"name {fm.get('name')!r} doesn't match folder {src.name!r}")
    for key in ("description", "license"):
        if not fm.get(key):
            problems.append(f"frontmatter {key} missing")
    for key in ("version", "last_reviewed", "applies_to", "audience", "finding_prefix", "modes"):
        if not meta.get(key):
            problems.append(f"metadata.{key} missing")
    prefix = meta.get("finding_prefix", "")
    if prefix and not PREFIX.match(prefix):
        problems.append(f"finding_prefix {prefix!r} must be 1-10 uppercase letters/digits")
    if prefix in prefixes:
        problems.append(f"finding_prefix {prefix!r} also used by {prefixes[prefix]}")
    prefixes.setdefault(prefix, src.name)
    headings = re.findall(r"^## (.+)$", text, re.M)
    expected = ORCHESTRATION_SECTIONS if orchestration else SECTIONS + PRODUCT_SECTIONS
    for section in expected:
        if not any(h.startswith(section) for h in headings):
            problems.append(f"SKILL.md has no '## {section}' section")
    if not orchestration and not build_dist.section(text, "Detection"):
        problems.append("Detection section is empty or not followed by '## ' or '---'")
    for part in PARTS:
        path = src / part
        if path.exists():
            for target in LINK.findall(path.read_text()):
                if not (path.parent / target).resolve().exists():
                    problems.append(f"{part}: broken link {target}")
    return problems


def main():
    prefixes, failed, count = {}, False, 0
    for skill_md in sorted(ROOT.glob("skills/*/*/SKILL.md")):
        count += 1
        problems = lint(skill_md.parent, prefixes)
        rel = skill_md.parent.relative_to(ROOT)
        for p in problems:
            print(f"{rel}: {p}")
        failed |= bool(problems)
    print(f"lint-skills: {count} skills checked, {'problems found' if failed else 'all OK'}.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
