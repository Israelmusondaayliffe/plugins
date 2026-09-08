# Generate an Astra prompt

Use when there is no source prompt.

1. Extract the job, intent, audience, success criteria, hard boundaries, available tools, side effects, output contract, and cost constraint.
2. Write the smallest prompt that preserves those requirements.
3. For interface work, include one scope-restraint line tied to the actual workflow. Do not prescribe a visual style unless the user supplied one.
4. For computer control, specify the target, allowed action boundary, completion condition, and evidence surface.
5. Leave model configuration unspecified until the target host proves exact values.
6. Validate and deliver using the shared template.
