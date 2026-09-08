#!/usr/bin/env python3
"""Check the approved package inventory and private writing exclusion."""
from pathlib import Path
import json,re,sys
root=Path(__file__).resolve().parent.parent
expected_writing={"writing-quality-router","writing-enforcer","business-writing-intent-enforcer","claim-boundary-checker"}
packages=root/"plugins"
actual={p.parent.name for p in (packages/"writing-quality/skills").glob("*/SKILL.md")}
errors=[]
if actual!=expected_writing: errors.append("Public Writing Quality must retain exactly its four existing skills")
if len(list(packages.glob("*/.codex-plugin/plugin.json")))!=29: errors.append("Public package inventory must remain at 29")
patterns=[re.compile("House of "+"Curiosity",re.I),re.compile(r"\bcw-[a-z][a-z-]+\b"),re.compile(r"Writing Like Me|Compound Writing",re.I),re.compile("personal-"+"plugins-private|claude-"+"plugins-private|"+"is"+"rael-plugins-private",re.I),re.compile(r"/(?:Users|home)/"+"is"+"rael"+"ayliffe",re.I)]
for path in packages.rglob("*"):
 if not path.is_file() or path.suffix.lower() not in {".md",".json",".py",".yaml",".yml",".sh",".toml",".txt"}: continue
 for line,text in enumerate(path.read_text(errors="replace").splitlines(),1):
  if any(pattern.search(text) for pattern in patterns): errors.append(f"Excluded private reference: {path.relative_to(root)}:{line}")
print(json.dumps({"ok":not errors,"writing_skills":sorted(actual),"errors":errors},indent=2))
sys.exit(bool(errors))
