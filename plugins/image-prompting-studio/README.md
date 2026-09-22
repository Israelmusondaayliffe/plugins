# Image Prompting Studio

Task-based image prompting, faithful reference translation, shared natural-language and structured templates, and Midjourney creation and edit prompts. This public package prepares prompts only; it does not generate images or run generation jobs.

Prompts are the default. Use the router or invoke a specialist directly. Model names live in dated profiles; refresh them on request. Brand Studio is not required.

Skills: image-prompt-router, image-prompt-create, image-prompt-edit, image-camera-directions, image-shot-planner, image-reference-composer, image-research-prompts, image-series, image-multi-output, image-typography, image-infographic, image-editorial, image-storyboard, image-campaign-grid, image-brand-interpretation, image-illustration-photo-translator, image-style-translator, image-time-variation, image-layout-architect, image-prompt-review, midjourney-prompt-architect, midjourney-edit-architect.

Public plugin for Claude Code, Claude Cowork, and Codex. The Codex manifest is `.codex-plugin/plugin.json` and the Claude manifest is `.claude-plugin/plugin.json`; both declare skills only. Validate this package with `python3 scripts/verify_bundle.py` (and `claude plugin validate .` where the Claude CLI is available). Source validation is separate from installed discovery and rendered-result review.

## Claude Code quick start

```text
/plugin marketplace add Israelmusondaayliffe/plugins
/plugin install image-prompting-studio@community-agent-plugins
```

Start a new task after installation. See [three example tasks](EXAMPLES.md), [support](SUPPORT.md) and [privacy](PRIVACY.md).

## License

MIT for original project material. Existing third-party licenses and notices remain in force. See [LICENSE](LICENSE).
