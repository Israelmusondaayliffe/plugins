---
name: eval-suite-builder
description: Use when defining how a skill or plugin should be tested. Builds ten positive and ten near-miss trigger cases, functional checks, and ground-truth rubric criteria without editing the target.
metadata:
  author: Community Maintainers
  version: 0.1.0
---

# Eval Suite Builder

1. Read the target `SKILL.md` files, manifest, scripts, and declared ownership.
2. Copy `assets/suite-template.json` to the target state directory created by the CLI.
3. Add at least ten positive trigger cases and ten near-miss negative cases. Use realistic language, paths, typos, and adjacent intents.
4. Add functional cases whose pass condition can be observed from files or commands.
5. Add judgment criteria only when each names an external source, original brief, or fixed checklist.
6. Keep case IDs stable across versions.
7. Validate from the plugin root:

```bash
python3 scripts/skill_eval_loop.py validate-suite /absolute/path/to/suite.json
```

Do not write assertions that merely check a file exists. Do not let the target author define success after seeing candidate output.
