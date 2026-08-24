"""
Runs the full data pipeline end to end and syncs outputs directly into the
dashboard's data folder. This is the single command the GitHub Action (and
you, locally) should run -- there is no manual copy-paste step.

Usage:
    python3 pipeline/run_pipeline.py
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone

STEPS = [
    "pipeline/generate_data.py",
    "pipeline/compute_variance.py",
    "pipeline/forecast_model.py",
]

SYNC_MAP = {
    "data/weekly_review.json": "dashboard/src/data/weeklyReview.json",
    "data/forecast_scenarios.json": "dashboard/src/data/forecastScenarios.json",
    "data/qa_examples.json": "dashboard/src/data/qaExamples.json",
}


def run_step(script):
    print(f"--- running {script} ---")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(f"Pipeline step failed: {script}")


def sync_outputs():
    for src, dest in SYNC_MAP.items():
        shutil.copy(src, dest)
        print(f"synced {src} -> {dest}")


def write_metadata():
    metadata = {"last_refreshed": datetime.now(timezone.utc).isoformat()}
    with open("dashboard/src/data/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"wrote refresh timestamp: {metadata['last_refreshed']}")


def main():
    for step in STEPS:
        run_step(step)
    sync_outputs()
    write_metadata()
    print("Pipeline complete. Dashboard data is up to date.")


if __name__ == "__main__":
    main()
