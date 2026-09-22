# Brand Studio

Brand strategy, briefs, identity systems and review using current brand context and independent creative judgment.

Works independently from Image Prompting Studio. Begin with current supplied or confirmed brand material; an explicitly named alternate brand remains valid.

Skills: brand-studio-router, brand-strategy, brand-brief, brand-identity-system, brand-review.

Public plugin for Claude Code, Claude Cowork, and Codex. The Codex manifest is `.codex-plugin/plugin.json` and the Claude manifest is `.claude-plugin/plugin.json`; both declare skills only. Validate this package with `python3 scripts/verify_bundle.py` (and `claude plugin validate .` where the Claude CLI is available). Source validation is separate from installed discovery and rendered-result review.

## Claude Code quick start

```text
/plugin marketplace add Israelmusondaayliffe/plugins
/plugin install brand-studio@community-agent-plugins
```

Start a new task after installation. See [three example tasks](EXAMPLES.md), [support](SUPPORT.md) and [privacy](PRIVACY.md).

## License

MIT for original project material. Existing third-party licenses and notices remain in force. See [LICENSE](LICENSE).
