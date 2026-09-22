# Three example tasks

These prompts are adapted from real work patterns. They are reusable demonstrations, not claims that this public version produced the original work. Provide the stated inputs before running each example.

## 1. Translate illustrations into photographic prompts

Inputs: Attach the illustrations you are authorized to use.

```text
Use image-prompting-studio:image-illustration-photo-translator on these illustrations. Write one photographic prompt per image that preserves the recognizable subject, pose, composition and world. Explain the material, light and texture changes needed for a photograph. Put each complete prompt in its own code block. Do not generate images.
```

Expected result: One faithful conversion prompt per reference, with important preservation constraints.

## 2. Prepare a coherent Midjourney still-life series

Inputs: Supply a product list or use a lamp, notebook and pen as sample subjects.

```text
Use image-prompting-studio:midjourney-prompt-architect to write a coherent product still-life series for these subjects. Keep the same surface, lighting logic and material treatment while choosing a suitable composition for each object. Use only supported Midjourney parameters and explain consequential choices. Put each prompt in a separate code block. Do not submit jobs.
```

Expected result: A coordinated set of Midjourney prompts; generation remains a separate user action.

## 3. Write realistic everyday scenes and a targeted edit

Inputs: Attach an authorized kitchen-scene image for the edit example and name your preferred image model, or accept broadly compatible language.

```text
Use image-prompting-studio:image-prompt-create to write realistic everyday-scene prompts: making coffee in a small kitchen, reading on a train, and browsing a market stall. Use natural light and an ordinary camera feel. Then use image-prompting-studio:image-prompt-edit to write an edit prompt for the attached kitchen image, moving that scene to a balcony while preserving the person. Deliver prompts only.
```

Expected result: Three creation prompts and one focused edit prompt, with no image-generation action.
