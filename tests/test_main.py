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
    assert "no tiene ninguna parada a una distancia máxima" in (session / "run.log").read_text(encoding="utf-8")
    with open(session / "summary.csv", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 2 and {r["seed"] for r in rows} and all(r["feasible"] == "True" for r in rows)
    # inst1 tiene óptimo probado (141.01); el gap se calcula respecto a él
    assert all(r["best_known"] == "141.01" and float(r["gap"]) >= -1e-4 for r in rows)

    run_csv = session / "config8" / "inst1-1s5-25-c25-w5" / "run_2.csv"
    replay = run_main("--replay", str(run_csv), "--output", str(tmp_path / "replays"), "--no-images")
    assert replay.returncode == 0, replay.stdout + replay.stderr
    assert "Resultado idéntico al original" in replay.stdout


def test_dry_run_lists_the_plan():
    result = run_main("--configs", "7", "8", "--pattern", "inst1-*", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "2 configuraciones × 1 instancias × 1 corridas = 2 ejecuciones" in result.stdout


def test_several_patterns_select_the_union_of_instances():
    result = run_main("--configs", "8", "--pattern", "inst54-*", "inst1-*", "--pattern", "inst54-*", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "1 configuraciones × 2 instancias" in result.stdout


def test_output_is_utf8_when_redirected():
    # Sin PYTHONIOENCODING, Windows escribiría la salida redirigida en cp1252
    env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONIOENCODING"}
    result = subprocess.run([sys.executable, str(ROOT / "app" / "main.py"), "--configs", "8", "--pattern", "inst1-*",
                             "--dry-run"], cwd=ROOT, capture_output=True, env=env)
    assert result.returncode == 0
    assert "configuraciones × 1 instancias".encode("utf-8") in result.stdout


def test_resume_runs_only_the_missing_runs(tmp_path):
    result = run_main("--configs", "8", "12", "--pattern", "inst1-*", "--runs", "2", "--population", "20",
                      "--max-iter", "3", "--workers", "2", "--no-images", "--output", str(tmp_path))
    assert result.returncode == 0, result.stderr
    session = next(tmp_path.iterdir())
    with open(session / "summary.csv", encoding="utf-8") as file:
        original = {(r["config"], r["run"]): r["value"] for r in csv.DictReader(file)}

    # Simula una interrupción: dos corridas sin terminar y sin resumen
    for path in [session / "config8" / "inst1-1s5-25-c25-w5" / "run_2.csv",
                 session / "config12" / "inst1-1s5-25-c25-w5" / "run_1.csv", session / "summary.csv"]:
        path.unlink()
    resumed = run_main("--resume", str(session), "--workers", "2")
    assert resumed.returncode == 0, resumed.stderr
    assert "2 corridas terminadas, 2 pendientes" in resumed.stdout

    with open(session / "summary.csv", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert {(r["config"], r["run"]): r["value"] for r in rows} == original
    manifest = json.loads((session / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "finished" and manifest["completed"] == 4 and len(manifest["resumed"]) == 1


def test_grid_runs_every_combination_with_common_seeds(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "app" / "grid.py"), "--pattern", "inst1-*", "inst5-*", "--runs", "2",
         "--population", "20", "--max-iter", "2", "--workers", "2", "--output", str(tmp_path),
         "--only", "stop_assign_strategy=H_STUDENT_TO_CLOSEST_STOP_STRATEGY",
         "route_generator_strategy=RANDOM_ROUTE_GENERATION_STRATEGY", "selection_operator=TOURNAMENT_SELECTION_OPERATOR",
         "crossover_operator=BCRC_CROSSOVER_OPERATOR_SBRP,EAX_CROSSOVER_OPERATOR_SBRP"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "12 combinaciones (1 stop × 1 route × 1 selection × 2 crossover × 6 mutation)" in result.stdout

    session = next(tmp_path.iterdir())
    with open(session / "grid.csv", encoding="utf-8") as file:
        grid = list(csv.DictReader(file))
    assert len(grid) == 12 and len({(g["crossover_operator"], g["mutation_operator"]) for g in grid}) == 12
    with open(session / "summary.csv", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 12 * 2 * 2 and all(r["feasible"] == "True" for r in rows)
    # Misma semilla para la misma instancia y corrida en todas las combinaciones
    seeds = {}
    for r in rows:
        seeds.setdefault((r["instance"], r["run"]), set()).add(r["seed"])
    assert len(seeds) == 4 and all(len(s) == 1 for s in seeds.values())
    config = json.loads((session / "configs" / "config1.json").read_text(encoding="utf-8"))
    assert config["max_stagnation_iter"] > config["max_iter"] == 2
