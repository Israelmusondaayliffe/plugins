# Unslop Harness Repair Worker Contract

## Topology

Use zero to three direct worker agents through the host's native agent surface. Use the smallest number that gives genuinely disjoint repair scopes. Do not launch a worker for ceremony or for work the parent can complete safely.

Recursive launches are forbidden. A worker cannot summon another worker.

The parent owns:

- scope and freeze;
- approval state;
- worker count and assignments;
- cross-scope decisions;
- integrated diff and ledger;
- installation and routing promotion;
- the completion verdict and user report.

Workers return evidence. They do not approve, integrate, install, publish, change registries, or declare completion.

## Dispatch packet

Each worker receives a bounded packet:

```json
{
  "run_id": "RUN_ID",
  "worker_id": "worker-1",
  "owned_paths": ["/absolute/approved/path"],
  "frozen_hashes": {"/absolute/approved/path": "SHA256"},
  "unslop_engine_sha256": "PINNED_ENGINE_SHA256",
  "accepted_finding_ids": ["F-001"],
  "protected_categories": [
    "code",
    "commands",
    "prompts",
    "quotations",
    "links",
    "paths",
    "identifiers",
    "tables",
    "frontmatter"
  ],
  "authority": {
    "may_edit_owned_paths": true,
    "may_expand_scope": false,
    "may_launch_workers": false,
    "may_integrate": false,
    "may_install": false,
    "may_publish": false,
    "may_declare_complete": false
  },
  "stop_conditions": [
    "hash drift",
    "out-of-scope dependency",
    "protected-material conflict",
    "ambiguous source intent",
    "no reduction in unresolved work"
  ]
}
```

Owned paths must be disjoint. Parent and worker must recheck the current hash before the first edit. A mismatch stops the assignment.

Each worker uses only the bundled engine under `unslop-harness-repair`. Writing Quality cannot supply policy, scanning, approval, or completion authority. The worker records its local scan and voice-preservation evidence in `tests` or `risks`.

## Return packet

Each worker returns:

```json
{
  "run_id": "RUN_ID",
  "unslop_engine_sha256": "PINNED_ENGINE_SHA256",
  "worker_id": "worker-1",
  "owned_paths": ["/absolute/approved/path"],
  "status": "complete",
  "changed_paths": ["/absolute/approved/path"],
  "finding_dispositions": [
    {
      "id": "F-001",
      "state": "repaired",
      "evidence": "concise evidence"
    }
  ],
  "residuals": [],
  "tests": ["exact command and result"],
  "unresolved_count": 0,
  "recursive_launches": 0,
  "risks": []
}
```

`complete` means the worker finished its assigned scope. It does not mean the repair run is complete.

## Parent reconciliation

The parent rejects a return packet when:

- a changed path is not owned by that worker;
- two workers own overlapping paths;
- a frozen hash changed before the worker edit;
- a worker launched another worker;
- protected material changed;
- the bundled engine digest differs from the parent's frozen digest;
- a worker depends on Writing Quality instead of the bundled engine;
- a finding lacks evidence or a terminal state;
- unresolved work did not fall;
- the worker claims approval, integration, installation, or completion authority.

The parent restores an edit only when the freeze proves it belongs to this run. Pre-existing user changes remain untouched.
