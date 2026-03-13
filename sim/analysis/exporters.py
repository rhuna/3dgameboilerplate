from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sim.analysis.recorder import MetricsRecorder


def export_metrics_csv(recorder: MetricsRecorder, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = recorder.as_dicts()
    fieldnames = [
        "step",
        "population",
        "average_temperature",
        "total_resources",
        "agent_productivity",
        "step_duration_ms",
        "error_count",
    ]

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return path


def export_metrics_json(recorder: MetricsRecorder, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "summary": recorder.summary(),
        "history": recorder.as_dicts(),
    }

    with path.open("w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2)

    return path