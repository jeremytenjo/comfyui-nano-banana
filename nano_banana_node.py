"""ComfyUI custom node for Nano Banana Pro image generation via Gemini API."""

from __future__ import annotations

import base64
import logging
from io import BytesIO
from typing import Any

import numpy as np
import requests
import torch
from PIL import Image

logger = logging.getLogger(__name__)


class NanoBananaProImage:
    """Generate an image from a prompt using Gemini Nano Banana Pro."""

    API_URL = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3-pro-image-preview:generateContent"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "display": "API Key",
                    },
                ),
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
            },
            "optional": {
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "api/image"

    def generate_image(self, api_key: str, prompt: str, image: torch.Tensor | None = None):
        api_key = (api_key or "").strip()
        prompt = (prompt or "").strip()

        if not api_key:
            raise ValueError("api_key is required")
        if not prompt:
            raise ValueError("prompt is required")

        parts: list[dict[str, Any]] = []
        if image is not None:
            image_bytes = self._comfy_tensor_to_png_bytes(image)
            parts.append(
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": base64.b64encode(image_bytes).decode("utf-8"),
                    }
                }
            )
        parts.append({"text": prompt})

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
            },
        }

        try:
            response = requests.post(
                f"{self.API_URL}?key={api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=120,
            )
        except requests.exceptions.RequestException as exc:
            logger.exception("Nano Banana API request failed")
            raise RuntimeError(f"Nano Banana API request failed: {exc}") from exc

        if not response.ok:
            message = self._extract_error_message(response)
            logger.warning("Nano Banana API error status=%s message=%s", response.status_code, message)
            raise RuntimeError(f"Nano Banana API error ({response.status_code}): {message}")

        try:
            data = response.json()
        except ValueError as exc:
            logger.exception("Failed to parse Nano Banana API JSON response")
            raise RuntimeError("Nano Banana API returned invalid JSON") from exc

        image_bytes = self._extract_first_image_bytes(data)
        image_tensor = self._bytes_to_comfy_tensor(image_bytes)
        return (image_tensor,)

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            return payload.get("error", {}).get("message") or response.text[:500] or "unknown error"
        except ValueError:
            return response.text[:500] or "unknown error"

    @staticmethod
    def _extract_first_image_bytes(payload: dict[str, Any]) -> bytes:
        candidates = payload.get("candidates") or []
        for candidate in candidates:
            parts = (candidate.get("content") or {}).get("parts") or []
            for part in parts:
                inline_data = part.get("inlineData") or {}
                mime_type = (inline_data.get("mimeType") or "").lower()
                b64_data = inline_data.get("data")
                if mime_type.startswith("image/") and b64_data:
                    try:
                        return base64.b64decode(b64_data)
                    except (ValueError, TypeError) as exc:
                        raise RuntimeError("Nano Banana returned invalid base64 image data") from exc

        raise RuntimeError("Nano Banana did not return an image in the response")

    @staticmethod
    def _bytes_to_comfy_tensor(image_bytes: bytes) -> torch.Tensor:
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                image = img.convert("RGB")
        except Exception as exc:
            raise RuntimeError("Failed to decode image bytes from Nano Banana response") from exc

        array = np.array(image).astype(np.float32) / 255.0
        return torch.from_numpy(array).unsqueeze(0)

    @staticmethod
    def _comfy_tensor_to_png_bytes(image: torch.Tensor) -> bytes:
        if image.ndim != 4:
            raise ValueError("Expected IMAGE tensor with shape [B, H, W, C]")
        sample = image[0].detach().cpu().numpy()
        sample = np.clip(sample, 0.0, 1.0)
        sample = (sample * 255.0).astype(np.uint8)
        pil_image = Image.fromarray(sample)
        output = BytesIO()
        pil_image.save(output, format="PNG")
        return output.getvalue()


NODE_CLASS_MAPPINGS = {
    "NanoBananaProImage": NanoBananaProImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBananaProImage": "Nano Banana Pro",
}
