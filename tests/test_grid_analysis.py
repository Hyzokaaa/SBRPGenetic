import csv

import pandas as pd
import pytest

from src.analysis import grid_analysis


@pytest.mark.parametrize("x, df, p", [(3.841459, 1, 0.05), (18.307038, 10, 0.05), (124.342113, 100, 0.05),
                                      (6.634897, 1, 0.01), (0.0, 3, 1.0), (1.0, 2, 0.606531)])
def test_chi2_survival_matches_tables(x, df, p):
    assert grid_analysis.chi2_sf(x, df) == pytest.approx(p, abs=1e-5)


def synthetic_runs(blocks=6):
    # A siempre mejor que B, y B mejor que C, en cada bloque (instancia, corrida)
    rows = []
    for block in range(blocks):
        for config, gap, crossover in (("config1", 0.10, "X"), ("config2", 0.20, "X"), ("config3", 0.30, "Y")):
            rows.append({"config": config, "instance": f"inst{block // 2}", "run": block % 2 + 1, "gap": gap + block / 100,
                         "execution_time": 1.0, "crossover_operator": crossover})
    return pd.DataFrame(rows)


def test_ranking_orders_by_mean_rank_and_detects_differences():
    table, friedman = grid_analysis.ranking(synthetic_runs(), ["crossover_operator"])
    assert table["config"].tolist() == ["config1", "config2", "config3"]
    assert table["rango_medio"].tolist() == [1.0, 2.0, 3.0]
    # Friedman con rangos perfectamente consistentes: estadístico N(k-1) = 12
    assert friedman["statistic"] == pytest.approx(12.0) and friedman["p_value"] < 0.01
    p = table.set_index("config")["p_holm"]
    assert pd.isna(p["config1"]) and p["config3"] < p["config2"]


def test_incomplete_blocks_are_left_out_of_the_ranking():
    runs = synthetic_runs()
    runs = runs[~((runs["config"] == "config3") & (runs["instance"] == "inst0"))]
    assert grid_analysis.complete_blocks(runs).groupby(grid_analysis.BLOCK).ngroups == 4


def test_factor_effects_and_interaction():
    runs = synthetic_runs()
    effects = grid_analysis.factor_effects(runs, "crossover_operator")
    assert effects.index.tolist() == ["X", "Y"]
    assert effects.loc["X", "mejor_combinación"] == pytest.approx(runs[runs["config"] == "config1"]["gap"].mean())
    assert grid_analysis.interaction(runs.assign(m="M"), "crossover_operator", "m").shape == (2, 1)


def test_load_reads_unfinished_launches(tmp_path):
    (tmp_path / "grid.csv").write_text("config,crossover_operator\nconfig1,X\n", encoding="utf-8")
    run_dir = tmp_path / "config1" / "inst54-7s20-100-c50-w20"
    run_dir.mkdir(parents=True)
    with open(run_dir / "run_1.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["instance", "config", "run", "value", "execution_time"])
        writer.writeheader()
        writer.writerow({"instance": "inst54-7s20-100-c50-w20", "config": "config1", "run": 1, "value": 203.566,
                         "execution_time": 2.5})
    runs, factors = grid_analysis.load(tmp_path)
    assert factors == ["crossover_operator"] and runs.loc[0, "crossover_operator"] == "X"
    assert runs.loc[0, "gap"] == pytest.approx(203.566 / 185.06 - 1)
