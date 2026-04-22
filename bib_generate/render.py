from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

from .config import Layout, QrField, TextField
from .data import Runner
from .qr import make_qr


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    max_size: int,
    max_w: int,
    max_h: int,
    min_size: int = 10,
) -> ImageFont.FreeTypeFont:
    size = max_size
    while size >= min_size:
        font = ImageFont.truetype(font_path, size=size)
        w, h = _text_size(draw, text, font)
        if w <= max_w and h <= max_h:
            return font
        size -= 2
    return ImageFont.truetype(font_path, size=min_size)


def draw_text(img: Image.Image, text: str, spec: TextField, layout: Layout) -> None:
    if not text:
        return
    draw = ImageDraw.Draw(img)
    x1, y1, x2, y2 = spec.bbox
    box_w, box_h = x2 - x1, y2 - y1
    font_path = str(layout.resolve(spec.font))

    if spec.auto_shrink:
        font = _fit_font(draw, text, font_path, spec.font_size, box_w, box_h)
    else:
        font = ImageFont.truetype(font_path, size=spec.font_size)

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_w = right - left
    text_h = bottom - top

    if spec.align == "left":
        tx = x1 - left
    elif spec.align == "right":
        tx = x2 - text_w - left
    else:
        tx = x1 + (box_w - text_w) // 2 - left

    if spec.valign == "top":
        ty = y1 - top
    elif spec.valign == "bottom":
        ty = y2 - text_h - top
    else:
        ty = y1 + (box_h - text_h) // 2 - top

    draw.text((tx, ty), text, font=font, fill=spec.color)


def paste_qr(img: Image.Image, url: str, spec: QrField) -> None:
    x1, y1, x2, y2 = spec.bbox
    side = min(x2 - x1, y2 - y1)
    qr_img = make_qr(url, side, border=spec.border, fg_color=spec.fg_color, bg_color=spec.bg_color)
    ox = x1 + ((x2 - x1) - side) // 2
    oy = y1 + ((y2 - y1) - side) // 2
    img.paste(qr_img, (ox, oy))


def render_bib(template: Image.Image, runner: Runner, layout: Layout) -> Image.Image:
    canvas = template.copy()
    draw_text(canvas, runner.dorsal, layout.numero, layout)
    draw_text(canvas, runner.nombre, layout.nombre, layout)
    draw_text(canvas, runner.ritmo_objetivo, layout.ritmo, layout)
    paste_qr(canvas, runner.qr_url, layout.qr)
    return canvas
