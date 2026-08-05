# Security

## Reporting

Do not open a public issue for a suspected secret, credential exposure, or
high-impact vulnerability. Use GitHub's private vulnerability reporting feature
for this repository when available, or contact the repository owner privately.

Include the affected plugin, file path, impact, reproduction steps, and any safe
evidence that helps confirm the issue. Do not include live credentials.

## Secret handling

This repository does not intentionally include private API keys, access tokens,
cookies, or account credentials.

Plugins that need authentication expect users to provide credentials through
their own environment, tool configuration, or connector. Never commit local
environment files or copied credentials.

Some third-party clients include documented public application identifiers or
guest credentials that are not account secrets. Treat them as service-specific
implementation details and follow the provider's current terms.

## Installation boundary

Review a plugin before installing it. Plugin skills can direct the active host to read
files, run scripts, or call configured tools within the authority of the active
task. Installation does not grant authority for unrelated external actions.
