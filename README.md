# bib-generate

Generador de dorsales personalizados para TEMPO RUN.

Toma un diseño base (JPG), un CSV/XLSX con corredores y un JSON de layout con coordenadas, y produce un JPG por corredor con número, QR (generado), nombre y ritmo objetivo.

## Instalación

```bash
uv sync            # o: pip install -e .
```

## Uso

```bash
python main.py generate \
  --runners examples/runners.csv \
  --layout examples/layout.json
```

Flags útiles:

- `--output DIR` override del directorio de salida
- `--dry-run` genera solo el primer dorsal (iterar coords rápido)
- `--filter-dorsal N` genera solo un dorsal específico

## Inputs

### 1. CSV/XLSX de corredores

Columnas requeridas (exactas):

| columna | ejemplo |
|---|---|
| `dorsal` | `42` |
| `nombre` | `Alejandro Olguín` |
| `ritmo_objetivo` | `5:30 min/km` o `Terminar` |
| `qr_url` | `https://tempo-run.com/r/<uuid>` |

### 2. Template JPG

Imagen base del dorsal (coloca el archivo en `examples/template.jpg` o donde referencie tu layout).

### 3. `layout.json`

Define el template, dpi, output_dir y la posición/estilo de cada campo. Coordenadas en píxeles absolutos (origen arriba-izquierda, igual que Figma):

```jsonc
{
  "template": "template.jpg",
  "output_dir": "../output",
  "dpi": 300,
  "fields": {
    "numero": { "bbox": [x1,y1,x2,y2], "font": "...", "font_size": 180, "color": "#000", "align": "center", "valign": "middle" },
    "qr":     { "bbox": [x1,y1,x2,y2], "border": 1, "fg_color": "#000", "bg_color": "#FFF" },
    "nombre": { "bbox": [...], "font": "...", "font_size": 48, "auto_shrink": true, "align": "center", "valign": "middle" },
    "ritmo":  { "bbox": [...], "font": "...", "font_size": 36, "color": "#E63946", "align": "center", "valign": "middle" }
  }
}
```

Ver ejemplo completo en `examples/layout.json`.

## Output

Archivos `dorsal_{NNN}_{slug-nombre}.jpg` a 300 DPI en el `output_dir` configurado.
