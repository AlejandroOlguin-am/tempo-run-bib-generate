from __future__ import annotations

import qrcode
from PIL import Image
from qrcode.constants import ERROR_CORRECT_M


def make_qr(
    url: str,
    size_px: int,
    border: int = 1,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
) -> Image.Image:
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_M,
        border=border,
        box_size=10,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")
    return img.resize((size_px, size_px), Image.NEAREST)
