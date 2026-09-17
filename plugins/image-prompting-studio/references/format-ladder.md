# Format choice

Natural language, JSON and system-style prompts all remain first-class formats. Preserve the user's choice. Choose by the work rather than a claim that one syntax reliably beats the others.

| Format | Useful when | Carry forward |
|---|---|---|
| Natural-language brief | An image, scene, mood or open exploration reads best as connected prose | Subject, action, environment, material/light, composition, meaningful constraints |
| JSON envelope | Surgical edits, reference roles, exact copy or constraints need separate addressable fields | `plan`, reference roles, scene fields, `preserve`, `changes`, relevant `forbidden`, `verify` |
| System-style operating prompt | One prompt requests a coherent set, or a reusable role turns a brief into image prompts | Shared visual DNA, image inventory, per-image directions, common checks |

The preserved [JSON recipes](json-envelope-template.md) and [system recipes](system-prompt-template.md) retain the user's detailed structures. Use only the needed variant. An XML role declaration can be pasted as a normal prompt on a chat surface; it is not necessarily a real system message. JSON is structured prompt text unless a current provider documents that exact native schema. ControlNet-like fields in inherited recipes are descriptive constraints, not proof of ControlNet execution.

PSGV is available in all three formats: PLAN gives composition intent, SEARCH supplies dated factual retrieval when needed, GENERATE is the visual brief, VERIFY names observable checks. These can be labels, JSON keys or XML blocks. Skip unnecessary labels in a short prompt. Do not treat an instruction to verify as actual verification evidence.

State format or what varies/holds when that helps compare alternatives. Do not turn routine prompts into an intake or always print a technical preamble. A forbidden list should address this brief's likely unwanted changes, without a numerical target. A shared operating prompt can request eight separate images when appropriate; actual delivery depends on the chosen model and host and must be checked.

## Additional formats and craft

The [general prompt templates](general-prompt-templates.md) retain scene, sticker, text, product, negative-space, comic, edit, inpaint and composition structures. The [eight Uni templates](uni-templates.md) include both prose and JSON. The [architect prompt skeleton](architect-prompt-skeleton.json) preserves a detailed subject/styling/environment/technical structure. It is a descriptive prompt skeleton, not a JSON Schema validator or API payload. Select relevant fields; do not impose people, skin, no-text or photorealism on unrelated subjects and media.

Use the [optional PSGV and axis preambles](psgv-recipes.md) when structure helps, and the [inherited system recipe](inherited-system-recipe.md) for its shared-DNA pattern. The [verbatim research library](verbatim-prompt-library.md) and [community examples](community-examples.md) are optional inspiration; source-recorded attribution is not fresh verification.
