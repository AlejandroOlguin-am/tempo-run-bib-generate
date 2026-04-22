from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TextField:
    bbox: tuple[int, int, int, int]
    font: str
    font_size: int
    color: str = "#000000"
    align: str = "center"   # left | center | right
    valign: str = "middle"  # top | middle | bottom
    auto_shrink: bool = False
    max_lines: int = 1


@dataclass
class QrField:
    bbox: tuple[int, int, int, int]
    border: int = 1
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"


@dataclass
class Layout:
    template: Path
    output_dir: Path
    dpi: int
    numero: TextField
    qr: QrField
    nombre: TextField
    ritmo: TextField
    base_dir: Path = field(default_factory=Path.cwd)

    def resolve(self, p: str | Path) -> Path:
        path = Path(p)
        return path if path.is_absolute() else (self.base_dir / path)


def _bbox(raw) -> tuple[int, int, int, int]:
    if not isinstance(raw, list) or len(raw) != 4:
        raise ValueError(f"bbox must be [x1, y1, x2, y2], got {raw!r}")
    x1, y1, x2, y2 = (int(v) for v in raw)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"bbox must have x2>x1 and y2>y1, got {raw!r}")
    return (x1, y1, x2, y2)


def _text_field(name: str, raw: dict) -> TextField:
    for required in ("bbox", "font", "font_size"):
        if required not in raw:
            raise ValueError(f"field '{name}' missing required key '{required}'")
    return TextField(
        bbox=_bbox(raw["bbox"]),
        font=raw["font"],
        font_size=int(raw["font_size"]),
        color=raw.get("color", "#000000"),
        align=raw.get("align", "center"),
        valign=raw.get("valign", "middle"),
        auto_shrink=bool(raw.get("auto_shrink", False)),
        max_lines=int(raw.get("max_lines", 1)),
    )


def _qr_field(raw: dict) -> QrField:
    if "bbox" not in raw:
        raise ValueError("field 'qr' missing required key 'bbox'")
    return QrField(
        bbox=_bbox(raw["bbox"]),
        border=int(raw.get("border", 1)),
        fg_color=raw.get("fg_color", "#000000"),
        bg_color=raw.get("bg_color", "#FFFFFF"),
    )


def load_layout(path: str | Path) -> Layout:
    path = Path(path).resolve()
    base_dir = path.parent
    raw = json.loads(path.read_text(encoding="utf-8"))

    for key in ("template", "fields"):
        if key not in raw:
            raise ValueError(f"layout missing '{key}'")

    fields = raw["fields"]
    for fname in ("numero", "qr", "nombre", "ritmo"):
        if fname not in fields:
            raise ValueError(f"layout.fields missing '{fname}'")

    template = Path(raw["template"])
    if not template.is_absolute():
        template = base_dir / template
    if not template.exists():
        raise FileNotFoundError(f"template not found: {template}")

    output_dir = Path(raw.get("output_dir", "output"))
    if not output_dir.is_absolute():
        output_dir = base_dir / output_dir

    layout = Layout(
        template=template,
        output_dir=output_dir,
        dpi=int(raw.get("dpi", 300)),
        numero=_text_field("numero", fields["numero"]),
        qr=_qr_field(fields["qr"]),
        nombre=_text_field("nombre", fields["nombre"]),
        ritmo=_text_field("ritmo", fields["ritmo"]),
        base_dir=base_dir,
    )

    for f in (layout.numero, layout.nombre, layout.ritmo):
        font_path = layout.resolve(f.font)
        if not font_path.exists():
            raise FileNotFoundError(f"font not found: {font_path}")

    return layout
