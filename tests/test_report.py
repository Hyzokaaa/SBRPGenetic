import csv
import subprocess
import sys

import pandas as pd
import pytest

from conftest import ROOT
from src.analysis import report


def test_wilcoxon_matches_the_normal_approximation_of_a_classic_example():
    # Datos de Darwin (diferencias de altura entre plantas): W+ = 96, n = 15 → z = 2.045, p bilateral ≈ 0.0409
    differences = [6, 8, 14, 16, 23, 24, 28, 29, 41, -48, 49, 56, 60, -67, 75]
    assert report.wilcoxon(pd.Series(differences), pd.Series([0] * 15)) == pytest.approx(0.0409, abs=5e-4)
    assert report.wilcoxon(pd.Series([1, 2, 3]), pd.Series([1, 2, 3])) == 1.0


def test_outcome_counts_wins_ties_and_losses():
    result = report.outcome(pd.Series([90.0, 100.0, 100.02, 110.0]), pd.Series([100.0, 100.0, 100.0, 100.0]))
    assert (result["mejor"], result["igual"], result["peor"]) == (1, 2, 1)
    assert result["diferencia_media"] == pytest.approx((-0.1 + 0 + 0.0002 + 0.1) / 4)


def write_launch(folder, rows):
    folder.mkdir(parents=True)
    with open(folder / "summary.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["config", "instance", "run", "seed", "value", "feasible",
                                                  "execution_time"])
        writer.writeheader()
        writer.writerows(rows)


def example_rows(config, factor):
    # inst1 tiene óptimo probado 141.01; inst113 solo el valor de la tesis (4511.55)
    return [{"config": config, "instance": instance, "run": run, "seed": run, "value": value * factor * (1 + run / 1000),
             "feasible": True, "execution_time": 2.0}
            for instance, value in (("inst1-1s5-25-c25-w5", 141.01), ("inst113-4s80-1600-c25-w5", 4400.0))
            for run in (0, 1)]


def test_quality_and_new_best_known(tmp_path):
    write_launch(tmp_path / "a", example_rows("config1", 1.0))
    table = report.per_instance(report.load_runs([tmp_path / "a"]))
    quality = report.quality(table).iloc[0]
    assert quality["igualan_mejor_conocido"] == 1 and quality["óptimos_alcanzados"] == 1 and quality["nuevos_mejores"] == 1
    new = report.new_best_known(table)
    assert list(new["instance"]) == ["inst113-4s80-1600-c25-w5"] and new["respeta_cota"].all()
    assert set(table["w"]) == {5} and set(table["paradas"]) == {5, 80}


def test_report_command_writes_every_format(tmp_path):
    write_launch(tmp_path / "a", example_rows("config1", 1.0))
    write_launch(tmp_path / "b", example_rows("config2", 1.05))
    output = tmp_path / "informe"
    result = subprocess.run([sys.executable, str(ROOT / "app" / "report.py"), str(tmp_path / "a"), str(tmp_path / "b"),
                             "--output", str(output), "--no-pdf"], cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8")
    assert result.returncode == 0, result.stderr
    for name in ("report.md", "report.html", "calidad.csv", "antecedentes.csv", "por_w.csv", "entre_configuraciones.csv",
                 "gap_por_w.png", "gaps_ordenados.png"):
        assert (output / name).exists(), name
    markdown = (output / "report.md").read_text(encoding="utf-8")
    assert ". Comparación entre configuraciones" in markdown and "| config1 |" in markdown
    html = (output / "report.html").read_text(encoding="utf-8")
    assert html.startswith("<!doctype html>") and "data:image/png;base64," in html
    pairs = pd.read_csv(output / "entre_configuraciones.csv")
    assert (pairs.loc[0, "mejor"], pairs.loc[0, "peor"]) == (2, 0)
