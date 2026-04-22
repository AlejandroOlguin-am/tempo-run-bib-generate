from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ("dorsal", "nombre", "ritmo_objetivo", "qr_url")


@dataclass
class Runner:
    dorsal: str
    nombre: str
    ritmo_objetivo: str
    qr_url: str


def load_runners(path: str | Path) -> list[Runner]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"runners file not found: {path}")

    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, dtype=str)
    elif suffix == ".csv":
        df = pd.read_csv(path, dtype=str)
    else:
        raise ValueError(f"unsupported extension {suffix!r}; use .csv or .xlsx")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"missing required columns: {missing}. Found: {list(df.columns)}"
        )

    df = df.fillna("")
    runners: list[Runner] = []
    for idx, row in df.iterrows():
        dorsal = str(row["dorsal"]).strip()
        nombre = str(row["nombre"]).strip()
        qr_url = str(row["qr_url"]).strip()
        if not dorsal or not nombre or not qr_url:
            raise ValueError(
                f"row {idx + 2}: dorsal, nombre and qr_url are required (got "
                f"dorsal={dorsal!r}, nombre={nombre!r}, qr_url={qr_url!r})"
            )
        runners.append(
            Runner(
                dorsal=dorsal,
                nombre=nombre,
                ritmo_objetivo=str(row["ritmo_objetivo"]).strip(),
                qr_url=qr_url,
            )
        )
    return runners
