from __future__ import annotations

import json
from pathlib import Path

from sim.replay.models import ReplayData


def save_replay(path: str | Path, replay: ReplayData) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(replay.to_dict(), f, indent=2)

    return out_path


def load_replay(path: str | Path) -> ReplayData:
    in_path = Path(path)

    with in_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    return ReplayData.from_dict(payload)