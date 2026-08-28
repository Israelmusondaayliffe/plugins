# Attribution

This package distributes the MIT-licensed `mvanhorn/last30days-skill` research engine with a public multi-host wrapper.

- Original author: Matt Van Horn
- Original source: https://github.com/mvanhorn/last30days-skill
- Pinned release: `v3.16.0`
- Pinned commit: `249c7a4c040558a903d6838dee31012980d4946d`
- Original copyright: Copyright (c) 2026 Matt Van Horn
- Public adapter and packaging: Community Maintainers, 2026

The complete upstream MIT license is included in `LICENSE`. The research engine under `skills/last30days/**` is frozen for this catalog port except for five unreferenced example-media files. Those files are omitted because they lack file-specific redistribution evidence, and one carries embedded location metadata. This exclusion does not change the research runtime.

Five files in the frozen subtree contain the local multi-host adaptation studied during the ownership audit:

- `skills/last30days/SKILL.md`
- `skills/last30days/agents/openai.yaml`
- `skills/last30days/references/save-html-brief.md`
- `skills/last30days/scripts/lib/html_render.py`
- `skills/last30days/scripts/lib/render.py`

The standalone `last30days` package is the catalog's canonical package for this pinned v3.16.0-derived line. The copy inside `founder-revenue-engine` is a separate frozen legacy snapshot. It is not the standalone source and is not synchronized automatically.

The bundled bird-search component retains its own MIT license at `skills/last30days/scripts/lib/vendor/bird-search/LICENSE`.
