# comfyui-nano-banana

ComfyUI custom node that calls **Nano Banana Pro** (`gemini-3-pro-image-preview`) through Google AI Studio REST and returns an `IMAGE` output.

## Inputs

- `api_key` (`STRING`, required): Google AI Studio API key.
- `prompt` (`STRING`, required): Prompt to generate an image.
- `image` (`IMAGE`, optional): Input conditioning image sent to the model.
- `image_name` (`STRING`, optional): Name/identifier used for local cache keying.

## Output

- `image` (`IMAGE`): The first generated image returned by the API.

## Install

1. Place this folder at `custom_nodes/comfyui-nano-banana`.
2. Install dependencies:

```bash
cd custom_nodes/comfyui-nano-banana
pip install -r requirements.txt
```

3. Restart ComfyUI.

## Notes

- This node uses direct API key access (no Comfy API proxy).
- If the API returns multiple images, this node returns the first one.
- The node caches outputs in memory by `(image_name, image_size, prompt)` and skips API calls on cache hits.
