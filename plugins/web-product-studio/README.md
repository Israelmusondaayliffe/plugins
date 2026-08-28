# Web Product Studio

Web Product Studio coordinates coherent frontend and web app work from brief through rendered verification.

## Owned skills

- web-product-router
- design-constitution-selector
- acceptance-flow
- code-production-agent
- full-output-enforcement
- image-to-code
- imagegen-frontend-web
- redesign-existing-projects
- visual-fidelity-gate (hidden, explicit or router-routed only)
- gstack
- playwright

## Optional design companions

- design-taste-frontend
- gpt-taste
- hallmark
- high-end-visual-design
- industrial-brutalist-ui
- minimalist-ui
- stitch-design-taste

These style skills are not bundled. The selector loads exactly one when needed.

## Optional platform companions

- Build Web Apps
- Supabase
- GitHub
- Security review tooling: Codex Security on Codex, the security review command on Claude Code
- Browser tooling (the in-app browser pane on Claude Code, the built-in Browser on Codex), with Playwright for repeatable automation and diagnostics

All companions are optional. Web Product Studio keeps route selection, code production, acceptance-flow design, and file verification inside this plugin. Without a browser surface, it reports the implementation and test evidence, marks rendered and visual acceptance incomplete, and names the exact browser proof still required. Without an authorized output root, it returns that status in the current task instead of writing a file.

## Boundaries

- Do not load multiple broad visual constitutions.
- Diagnostic requests do not authorize implementation.
- Rendered browser flows are the primary completion surface for user-facing behavior. File and test checks cannot replace them.
- For likeness-dependent or picture-led work, the router invokes the hidden visual-fidelity-gate specialist before secondary features. Functional completion and visual completion remain separate, and work below the visual threshold is reported as incomplete.

## Verification

Run scripts/verify_bundle.py, validate route and acceptance artifacts, then execute the named flows in the host browser surface: the in-app browser pane on Claude Code, the built-in Browser on Codex.
