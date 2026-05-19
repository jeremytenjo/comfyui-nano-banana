# comfyui-nano-banana

ComfyUI custom node that calls **Nano Banana Pro** (`gemini-3-pro-image-preview`) through Google AI Studio REST and returns an `IMAGE` output.

## Inputs

- `api_key` (`STRING`, required): Google AI Studio API key.
- `prompt` (`STRING`, required): Prompt to generate an image.
- `size` (`DROPDOWN`, required): Output aspect ratio with 1K pixel dimensions. Default: `9:16 (768x1344)`. Options: `1:1 (1024x1024)`, `2:3 (832x1248)`, `3:2 (1248x832)`, `3:4 (864x1184)`, `4:3 (1184x864)`, `4:5 (896x1152)`, `5:4 (1152x896)`, `9:16 (768x1344)`, `16:9 (1344x768)`, `21:9 (1536x672)`.
- `resolution` (`DROPDOWN`, required): Output image size. Options: `1K`, `2K`, `4K`.
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
- The node caches outputs in memory by `(image_name, image_size, prompt, size, resolution)` and skips API calls on cache hits.
