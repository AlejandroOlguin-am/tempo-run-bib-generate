from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import click
from PIL import Image

from .config import load_layout
from .data import load_runners
from .render import render_bib


def _slug(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-").lower()
    return ascii_text or "runner"


@click.group()
def cli() -> None:
    """bib-generate — generador de dorsales personalizados."""


@cli.command()
@click.option("--runners", "runners_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--layout", "layout_path", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "output_override", type=click.Path(file_okay=False), default=None)
@click.option("--dry-run", is_flag=True, help="Genera solo el primer dorsal.")
@click.option("--filter-dorsal", default=None, help="Genera solo el dorsal con este número.")
def generate(runners_path, layout_path, output_override, dry_run, filter_dorsal):
    """Genera N dorsales JPG a partir del CSV/XLSX y el layout."""
    layout = load_layout(layout_path)
    runners = load_runners(runners_path)

    if filter_dorsal is not None:
        runners = [r for r in runners if r.dorsal == str(filter_dorsal)]
        if not runners:
            raise click.ClickException(f"no runner with dorsal {filter_dorsal!r}")
    if dry_run:
        runners = runners[:1]

    out_dir = Path(output_override) if output_override else layout.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    template = Image.open(layout.template).convert("RGB")
    click.echo(f"Template: {layout.template} ({template.size[0]}x{template.size[1]})")
    click.echo(f"Output:   {out_dir}")
    click.echo(f"Runners:  {len(runners)}")

    if layout.output_size:
        click.echo(f"Resize:   {layout.output_size[0]}x{layout.output_size[1]}")

    with click.progressbar(runners, label="Generando dorsales") as bar:
        for runner in bar:
            img = render_bib(template, runner, layout)
            if layout.output_size:
                img = img.resize(layout.output_size, Image.LANCZOS)
            filename = f"dorsal_{str(runner.dorsal).zfill(3)}_{_slug(runner.nombre)}.jpg"
            img.save(out_dir / filename, "JPEG", quality=95, dpi=(layout.dpi, layout.dpi))

    click.echo(f"\n✓ {len(runners)} dorsal(es) generado(s) en {out_dir}")


if __name__ == "__main__":
    cli()
