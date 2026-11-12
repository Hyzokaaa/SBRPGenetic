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
