# Web product routes

- greenfield: new product or major new surface. Use code-production-agent and the Build Web Apps companion.
- redesign: improve an existing rendered interface. Use redesign-existing-projects.
- image-first: implement from a screenshot, mockup, or visual reference. Use image-to-code or imagegen-frontend-web.
- targeted-fix: scoped code or interaction repair. Use code-production-agent and full-output-enforcement as needed.
- quality-assurance: inspect behavior and rendering without implementing unless authorized. Use Playwright and the host browser surface (the in-app browser pane on Claude Code, the built-in Browser on Codex).

Add `visual-fidelity-gate` before general implementation when a route depends on a supplied or named visual reference, likeness, photorealism, cinematic or material realism, procedural graphics, shaders, WebGL, WebGPU, 3D, simulation, an immersive picture-led experience, or a motion-led hero. The route remains `greenfield`, `redesign`, or `image-first`; the gate is a required specialist and stop condition, not a competing primary route.

Do not add the gate merely because a routine product has colors, spacing, icons, charts, or a generic request to look clean.

Companions:

- GitHub for repository and pull request state.
- Supabase when the product uses it.
- Security review tooling for security-sensitive changes: Codex Security on Codex, the security review command on Claude Code.
- Browser tooling for rendered verification: the in-app browser pane on Claude Code, the built-in Browser on Codex.

For high-visual-stakes work, a running app, clean console, telemetry, labels, or complete feature list cannot replace a fresh same-size comparison. Freeze secondary features until an independent hero review reaches at least 7 out of 10 with no P0, P1, or P2 visual gap. Below that boundary, repair, switch method, or report the work as visually incomplete.

Do not load every design skill. Use design-constitution-selector and exactly one visual system when style work is required.
