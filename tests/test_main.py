import csv
import json
import shutil
import subprocess
import sys

import pytest

from conftest import INSTANCES, ROOT

pytestmark = pytest.mark.slow


def run_main(*args):
    return subprocess.run([sys.executable, str(ROOT / "app" / "main.py"), *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})


def test_batch_isolates_failures_and_replays_exactly(tmp_path):
    instances = tmp_path / "instances"
    instances.mkdir()
    shutil.copy(INSTANCES / "real" / "inst1-1s5-25-c25-w5.xpress", instances)
    shutil.copy(INSTANCES / "MH" / "2.xpress", instances)   # imposible: un estudiante sin parada alcanzable

    result = run_main("--configs", "8", "--instances", str(instances), "--runs", "2", "--population", "20",
                      "--max-iter", "3", "--workers", "2", "--no-images", "--output", str(tmp_path / "out"))
    assert result.returncode == 0, result.stderr

    session = next((tmp_path / "out").iterdir())
    manifest = json.loads((session / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "finished" and manifest["completed"] == 2 and manifest["failed"] == 2
    assert (session / "configs" / "config8.json").exists()
    assert (session / "errors.csv").exists()
    assert "no pudo ser asignado" in (session / "run.log").read_text(encoding="utf-8")
    with open(session / "summary.csv", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 2 and {r["seed"] for r in rows} and all(r["feasible"] == "True" for r in rows)

    run_csv = session / "config8" / "inst1-1s5-25-c25-w5" / "run_2.csv"
    replay = run_main("--replay", str(run_csv), "--output", str(tmp_path / "replays"), "--no-images")
    assert replay.returncode == 0, replay.stdout + replay.stderr
    assert "Resultado idéntico al original" in replay.stdout


def test_dry_run_lists_the_plan():
    result = run_main("--configs", "7", "8", "--pattern", "inst1-*", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "2 configuraciones × 1 instancias × 1 corridas = 2 ejecuciones" in result.stdout
