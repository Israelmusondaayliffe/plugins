---
name: video-production-router
description: Routes video requests to concept, script, prompt, footage, captions, overlays, motion graphics, music visualization, slideshow, product launch, PR, website capture, or runtime implementation. Use when a video brief spans multiple production skills or the correct production path is unclear. Produces a validated route and explicit runtime choice before asset generation or rendering begins.
---

# Video Production Router

## Overview

Turn a video brief into one primary production path and a short sequence of supporting skills. Choose the runtime only after the output format and evidence needs are clear.

## Workflow

1. Extract objective, audience, duration, aspect ratio, platform, source assets, and delivery format.
2. Choose one primary route using references/routing.md.
3. Record the decision in assets/route-template.json and run scripts/validate_route.py.
4. Check which production surfaces are installed and visible in the current task. HyperFrames, Remotion, Browser, Computer Use, and other external production surfaces are optional at runtime.
5. When a renderer is available, use HyperFrames as the preferred runtime for generated motion work. Use Remotion when the user requests it or the source project already depends on it. Preserve the selected runtime skill and its exact commands.
6. When no renderer is available, use the No-renderer planning path below. Do not load an absent companion or stop the planning work.
7. Load only the bundled skills needed for the selected sequence.
8. End every rendered delivery with video-delivery-qc.

## No-renderer planning path

Write a self-contained planning bundle inside the user-approved output root:

- `video-brief.md`: objective, audience, format, duration, aspect ratio, message, and constraints.
- `storyboard.md`: ordered scenes with purpose, content, timing, and transitions.
- `shot-list.md`: each planned shot, source or creation method, framing, duration, and status.
- `asset-ledger.md`: required and available media, provenance, rights or license state, and missing assets.
- `runtime-requirements.md`: renderer, capture, inspection, codec, font, and other production requirements still needed.
- `delivery-checklist.md`: planned export, audio, caption, technical, and visual checks.

Set `runtime` to `none`, `renderer_available` to `false`, and `completion_state` to `planning-complete`. Mark both `rendering_status` and `visual_qc_status` as `incomplete`. Planning can be complete without claiming that a video was rendered or visually checked.

## Completion states

- `planning-complete`: the six planning artifacts exist and agree. Rendering and visual QC remain incomplete.
- `rendered-delivery-complete`: an available renderer produced the delivery file and video-delivery-qc completed the technical and visual checks.

## Error Handling

- If required source media is missing, stop before inventing substitutes that change the brief.
- If platform dimensions are unknown, state the assumed target and keep the layout adaptable.
- If runtime ownership is unclear, choose a route before writing implementation code. Missing runtime access does not block the no-renderer planning path.

## Reliability Notes

The model selects and sequences creative skills. The validator enforces an allowed primary route, delivery dimensions, runtime availability, planning artifacts, and completion state. It rejects a rendered-delivery claim when rendering or visual QC is incomplete.

## Resources

- scripts/validate_route.py validates production routes.
- references/routing.md maps briefs to skills.
- assets/route-template.json records the decision.
