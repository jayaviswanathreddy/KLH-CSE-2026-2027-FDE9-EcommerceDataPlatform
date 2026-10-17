from pathlib import Path
import subprocess
import sys
from datetime import datetime


# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Pipeline stages
STAGES = [
    ("Data Ingestion", "src/ingest.py"),
    ("Data Transformation", "src/transform.py"),
    ("Data Warehouse Loading", "src/load.py"),
    ("Data Quality Checks", "src/data_quality.py"),
]


def run_stage(stage_name, script_path):
    """Run one pipeline stage."""

    print("\n" + "=" * 60)
    print(f"STARTING: {stage_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / script_path)],
        cwd=PROJECT_ROOT
    )

    if result.returncode != 0:
        print(f"\n❌ {stage_name} failed!")
        return False

    print(f"\n✅ {stage_name} completed successfully!")
    return True


def run_pipeline():
    """Run all pipeline stages in sequence."""

    start_time = datetime.now()

    print("\n🚀 E-COMMERCE DATA PIPELINE STARTED")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    for stage_name, script_path in STAGES:
        success = run_stage(stage_name, script_path)

        if not success:
            print("\n❌ Pipeline stopped because a stage failed.")
            return

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 60)
    print("🎉 COMPLETE PIPELINE EXECUTION SUCCESSFUL!")
    print("=" * 60)
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total execution time: {duration}")


if __name__ == "__main__":
    run_pipeline()