# Film Advisor Protocol v1

Film Advisor is this plugin's separate explicit runtime contract. It is not Agent Ops Sol Advisor and has no authority over that system.

## Activation

Accept only a deliberate `film-advisor` invocation, `/film-advisor`, `@ai-film-studio/film-advisor`, or a machine packet with `activation.mode: "explicit"` and `activation.invocation: "film-advisor"`.

Do not activate from a quoted name, a negated request, a conditional example, an incidental mention, or ordinary filmmaking language. Return ordinary conversation or the appropriate owner instead.

## Packet authority

Input conforms to `schemas/film-advisor-packet.schema.json`. The runtime may return only a route, a record request, a validation result, or a stopped approval gate. It cannot approve, integrate, install, publish, authenticate, upload, purchase, generate, or destructively replace material.

The runtime treats `project_root` and record paths as declarations. It does not create, delete, or alter project files. Parent systems own integration and final acceptance.

## Routes

`concept` routes to `film-wayfinder`; `brief` to `ai-film-studio`; `architecture` to `production-architect`; `assets` to `asset-bible-director`; `performance` to `performance-director`; `geography` to `visual-development-director`; `shots` to `shot-continuity-director`; `adapter` to `film-prompt-director`; `iteration` to `iteration-supervisor`; and `finish` to `post-delivery-director`. Any generic wayfinding or generic brief primitive is outside this protocol's authority.

## External stop

If an action in the packet is externally consequential, the runtime returns `stopped` unless the action has matching explicit approval. See [approval gates](approval-gates.md).
