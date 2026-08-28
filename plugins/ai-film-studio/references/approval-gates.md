# External-Action Approval Gates

Film Advisor may plan, draft, validate, and classify inside the supplied project scope. It must stop before any of the following external actions unless a packet contains a matching explicit approval:

| Action type | Minimum approval evidence |
| --- | --- |
| `paid_generation` | target surface, cost exposure, and approval ID |
| `account_authentication` | named account or surface and approval ID |
| `upload` | destination, files, and approval ID |
| `purchase` | vendor, amount or pricing exposure, and approval ID |
| `destructive_replacement` | exact target, recovery plan, and approval ID |
| `publication` | destination, public/private scope, and approval ID |
| `material_scope_expansion` | exact scope delta, cost preview, and approval ID |

An approval is scoped to one action and target. A previous approval does not authorize a new cost, upload, replacement, or publication. When approval is absent, return a stopped Film Advisor result that names the blocked action and the evidence required.
