import pytest

from conftest import INSTANCES
from src.analysis import best_known


def test_every_instance_has_a_reference():
    names = {path.stem for path in (INSTANCES / "real").glob("inst*.xpress")}
    assert set(best_known.load()) == names and len(names) == 120


def test_references_are_consistent():
    for name, record in best_known.load().items():
        values = [float(record[k]) for k in ("mip", "grasp_vnd", "hill_climbing_2020") if record[k]]
        assert record["best_known"] <= min(values) + 1e-9, name
        if record["lower_bound"]:
            assert record["best_known"] >= float(record["lower_bound"]) - 0.005, name
        if record["mip"]:
            assert record["optimal"] and record["best_known"] == float(record["mip"]), name
    assert sum(r["optimal"] for r in best_known.load().values()) == 59


def test_gap():
    assert best_known.reference("real/inst54-7s20-100-c50-w20.xpress")["best_known"] == 185.06
    assert best_known.gap(185.06 * 1.1, "inst54-7s20-100-c50-w20") == pytest.approx(0.1)
    assert best_known.gap(100, "mi_instancia") is None and best_known.gap(None, "inst1-1s5-25-c25-w5") is None
