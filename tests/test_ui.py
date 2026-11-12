import csv

import pytest

from conftest import ROOT

pytestmark = pytest.mark.slow

APP = str(ROOT / "app" / "ui" / "app.py")
PAGES = ["views/live_run.py", "views/operator_lab.py", "views/compare.py", "views/results.py"]


@pytest.fixture
def app():
    from streamlit.testing.v1 import AppTest
    return AppTest.from_file(APP, default_timeout=300).run()


def exceptions(at):
    return [str(e.value) for e in at.exception]


def test_every_page_loads(app):
    assert exceptions(app) == []
    for page in PAGES:
        app.switch_page(page).run()
        assert exceptions(app) == [], page


def test_live_run_produces_a_feasible_result(app):
    app.switch_page("views/live_run.py").run()
    inputs = {n.label: n for n in app.sidebar.number_input}
    inputs["Población"].set_value(30)
    inputs["Máx. generaciones"].set_value(5)
    next(b for b in app.sidebar.button if "Ejecutar" in b.label).click().run()
    assert exceptions(app) == []
    assert any("factible" in s.value for s in app.success)


def test_operator_lab_applies_crossover_and_mutation(app):
    app.switch_page("views/operator_lab.py").run()
    next(b for b in app.sidebar.button if b.label == "Generar población").click().run()
    for label in ("Aplicar cruce", "Mutar padre A"):
        next(b for b in app.button if b.label == label).click().run()
        assert exceptions(app) == [], label


def test_live_run_with_a_baseline_hides_ga_controls(app):
    app.switch_page("views/live_run.py").run()
    app.sidebar.selectbox[1].set_value("config11").run()
    labels = {n.label for n in app.sidebar.number_input}
    assert "Tamaño de torneo" not in labels and "Élite" not in labels
    inputs = {n.label: n for n in app.sidebar.number_input}
    inputs["Población"].set_value(20)
    inputs["Máx. generaciones"].set_value(3)
    next(b for b in app.sidebar.button if "Ejecutar" in b.label).click().run()
    assert exceptions(app) == []
    assert any("factible" in s.value for s in app.success)


def test_calibration_page_ranks_a_grid_launch(tmp_path, monkeypatch):
    launch = tmp_path / "20260101_000000"
    launch.mkdir()
    (launch / "grid.csv").write_text("config,crossover_operator,mutation_operator\n"
                                     "config1,BCRC_CROSSOVER_OPERATOR_SBRP,SWAP_MUTATION_OPERATOR_SBRP\n"
                                     "config2,EAX_CROSSOVER_OPERATOR_SBRP,SWAP_MUTATION_OPERATOR_SBRP\n", encoding="utf-8")
    with open(launch / "summary.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["config", "instance", "run", "value", "execution_time"])
        writer.writeheader()
        for run in (1, 2):
            for instance, optimum in (("inst1-1s5-25-c25-w5", 141.01), ("inst54-7s20-100-c50-w20", 185.06)):
                writer.writerow({"config": "config1", "instance": instance, "run": run, "value": optimum * 1.1,
                                 "execution_time": 1})
                writer.writerow({"config": "config2", "instance": instance, "run": run, "value": optimum * 1.3,
                                 "execution_time": 2})
    monkeypatch.setenv("SBRP_RESULTS_DIR", str(tmp_path))
    app_test = __import__("streamlit.testing.v1", fromlist=["AppTest"]).AppTest.from_file(APP, default_timeout=120).run()
    app_test.switch_page("views/calibration.py").run()
    assert exceptions(app_test) == []
    metrics = {m.label: m.value for m in app_test.metric}
    assert metrics["Combinaciones"] == "2" and metrics["Bloques completos"] == "4"
    assert metrics["Mejor gap medio"] == "+10.0%"
    assert any("Bcrc" in m.value for m in app_test.markdown)
