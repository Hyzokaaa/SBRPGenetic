"""
Ejecución por lotes del algoritmo genético.

Ejemplos (desde la raíz del proyecto):
    python app/main.py --configs 7 8 9 --pattern "inst5*" --runs 3
    python app/main.py --dry-run
    python app/main.py --replay results/20261111_193809/config7/inst54-7s20-100-c50-w20/run_2.csv
    python app/main.py --resume results/20261111_193809

Cada lanzamiento escribe en results/<fecha_hora>/ los resultados (config<N>/<instancia>/run_<k>.csv), una copia de las
configuraciones usadas, el manifiesto (manifest.json: argumentos, semillas, versión del código), el log (run.log),
el resumen (summary.csv) y las corridas fallidas (errors.csv).
"""
import argparse
import csv
import datetime as dt
import json
import logging
import logging.handlers
import multiprocessing
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.executor import run_single  # noqa: E402
from src.analysis import best_known  # noqa: E402
from src.utils.utils import get_string_config_data  # noqa: E402

CONFIGS_DIR = ROOT / "src" / "problems" / "problem_sbrp" / "algorithm" / "genetic_algorithm"
SUMMARY_COLUMNS = ["config", "instance", "run", "seed", "value", "best_known", "gap", "iteration", "execution_time",
                   "stop_reason", "stop_iteration", "feasible", "violations"]


# ------------------------- Utilidades -------------------------
def natural_key(text: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", text)]


def relative_to_root(path: Path) -> str:
    path = Path(path).resolve()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def resolve(path: str) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def git_info() -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                                    capture_output=True, text=True).stdout.strip())
        return {"commit": commit or None, "dirty": dirty}
    except OSError:
        return {"commit": None, "dirty": None}


def new_session_dir(output: Path, suffix: str = "") -> Path:
    name = dt.datetime.now().strftime("%Y%m%d_%H%M%S") + suffix
    session = output / name
    counter = 1
    while session.exists():
        session = output / f"{name}_{counter}"
        counter += 1
    session.mkdir(parents=True)
    return session


def write_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


# ------------------------- Procesos y log -------------------------
def worker_init(queue, level: int):
    """Inicializa cada proceso: backend gráfico sin ventana y log enviado al proceso principal."""
    import matplotlib
    matplotlib.use("Agg")
    root = logging.getLogger()
    root.handlers = [logging.handlers.QueueHandler(queue)]
    root.setLevel(level)


def run_job(job: dict) -> dict:
    """Ejecuta una corrida sin interrumpir el lote si falla."""
    try:
        record = run_single(job["config"], job["config_path"], job["instance_path"], job["run"], job["seed"],
                            job["output_dir"], job.get("save_image", True))
        return {"status": "ok", **with_reference(record, job["instance"])}
    except Exception as error:
        logging.getLogger(__name__).error(f"Falló {job['config']} · {job['instance']} · run {job['run']}: {error}")
        return {"status": "error", "config": job["config"], "instance": job["instance"], "run": job["run"],
                "seed": job["seed"], "error": f"{type(error).__name__}: {error}", "traceback": traceback.format_exc()}


def start_logging(session: Path, level: int):
    queue = multiprocessing.Queue()
    formatter = logging.Formatter("%(asctime)s - %(processName)s - %(levelname)s - %(name)s - %(message)s")
    file_handler = logging.FileHandler(session / "run.log", encoding="utf-8")
    console_handler = logging.StreamHandler()
    for handler in (file_handler, console_handler):
        handler.setFormatter(formatter)
    listener = logging.handlers.QueueListener(queue, file_handler, console_handler)
    listener.start()
    worker_init(queue, level)
    return queue, listener


def run_jobs(jobs: list, workers: int, queue, level: int) -> list:
    results = []
    start = time.time()
    with multiprocessing.Pool(processes=workers, initializer=worker_init, initargs=(queue, level)) as pool:
        for done, result in enumerate(pool.imap_unordered(run_job, jobs), 1):
            results.append(result)
            elapsed = time.time() - start
            remaining = elapsed / done * (len(jobs) - done)
            outcome = f"{result['value']:.2f}" if result["status"] == "ok" and result["value"] is not None \
                else ("sin solución" if result["status"] == "ok" else "ERROR")
            print(f"[{done}/{len(jobs)}] {result['config']} · {result['instance']} · run {result['run']} → {outcome} "
                  f"| transcurrido {dt.timedelta(seconds=int(elapsed))} · restante ~{dt.timedelta(seconds=int(remaining))}",
                  flush=True)
    return results


# ------------------------- Lote -------------------------
def find_instances(instances: str, patterns) -> list:
    instances_dir = resolve(instances)
    patterns = patterns or ["*.xpress"]
    found = sorted({p for pattern in patterns for p in instances_dir.glob(pattern) if p.is_file()},
                   key=lambda p: natural_key(p.name))
    if not found:
        sys.exit(f"No hay instancias que coincidan con {', '.join(repr(p) for p in patterns)} en {instances_dir}")
    return found


def create_session(args, configs: dict, instances: list, jobs: list, extra: dict = None) -> tuple:
    """
    Crea la carpeta del lanzamiento con la copia de cada configuración ({nombre: datos}) y el manifest.json,
    y completa cada corrida con las rutas que necesita para ejecutarse. Devuelve (carpeta, manifest).
    """
    session = new_session_dir(resolve(args.output))
    (session / "configs").mkdir()
    for config_name, config_data in configs.items():
        # Copia de la configuración usada, para poder reproducir y reanudar las corridas
        write_json(session / "configs" / f"{config_name}.json", config_data)
        (session / config_name).mkdir()
        with open(session / config_name / "config_params.txt", "w", encoding="utf-8") as file:
            file.write(get_string_config_data(str(session / "configs" / f"{config_name}.json")) + "\n")

    manifest = {
        "started": dt.datetime.now().isoformat(timespec="seconds"), "status": "running",
        "arguments": {key: value for key, value in vars(args).items() if key not in ("replay", "resume")},
        "code": git_info(), "python": platform.python_version(),
        "configs": {name: f"configs/{name}.json" for name in configs},
        "instances": {p.stem: relative_to_root(p) for p in instances},
        "save_images": not args.no_images,
        **(extra or {}),
        "runs": [{k: job[k] for k in ("config", "instance", "run", "seed")} for job in jobs],
    }
    write_json(session / "manifest.json", manifest)
    complete_jobs(session, manifest, jobs)
    return session, manifest


def complete_jobs(session: Path, manifest: dict, jobs: list):
    for job in jobs:
        job["config_path"] = str(session / manifest["configs"][job["config"]])
        job["instance_path"] = str(resolve(manifest["instances"][job["instance"]]))
        job["output_dir"] = str(session)
        job["save_image"] = manifest.get("save_images", not manifest.get("arguments", {}).get("no_images", False))


def run_csv(session: Path, job: dict) -> Path:
    return session / job["config"] / job["instance"] / f"run_{job['run']}.csv"


def completed_record(session: Path, job: dict):
    """Resultado de una corrida ya terminada (leído de su run_<k>.csv), o None si no terminó."""
    try:
        with open(run_csv(session, job), encoding="utf-8") as file:
            row = next(csv.DictReader(file))
    except (OSError, StopIteration):
        return None
    value = float(row["value"]) if row.get("value") not in (None, "", "None") else None
    record = {**row, "status": "ok", "value": value, "run": int(row["run"]), "seed": int(row["seed"]),
              "feasible": row.get("feasible") == "True"}
    return with_reference(record, job["instance"])


def with_reference(record: dict, instance: str) -> dict:
    reference = best_known.reference(instance)
    gap = best_known.gap(record["value"], instance)
    return {**record, "best_known": reference["best_known"] if reference else None,
            "gap": round(gap, 6) if gap is not None else None}


def execute_session(session: Path, manifest: dict, jobs: list, args, previous: list = ()):
    """Ejecuta las corridas pendientes del lanzamiento y escribe summary.csv con todas las terminadas."""
    queue, listener = start_logging(session, getattr(logging, args.log_level))
    start = time.time()
    try:
        results = list(previous) + run_jobs(jobs, args.workers, queue, getattr(logging, args.log_level))
    finally:
        listener.stop()

    ok = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] == "error"]
    key = lambda r: (natural_key(r["config"]), natural_key(r["instance"]), r["run"])
    with open(session / "summary.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(ok, key=key))
    if failed:
        with open(session / "errors.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["config", "instance", "run", "seed", "error", "traceback"],
                                    extrasaction="ignore")
            writer.writeheader()
            writer.writerows(sorted(failed, key=key))

    manifest.update({"status": "finished", "finished": dt.datetime.now().isoformat(timespec="seconds"),
                     "duration_seconds": round(manifest.get("duration_seconds", 0) + time.time() - start, 1),
                     "completed": len(ok), "failed": len(failed)})
    write_json(session / "manifest.json", manifest)

    print(f"\nTerminado en {dt.timedelta(seconds=int(time.time() - start))}: {len(ok)} correctas, {len(failed)} fallidas")
    configs = list(manifest["configs"])
    shown = configs if len(configs) <= 20 else []
    if not shown:
        print(f"  {len(configs)} configuraciones: el resumen por configuración está en summary.csv")
    for config_name in shown:
        values = [r["value"] for r in ok if r["config"] == config_name and r["value"] is not None]
        gaps = [r["gap"] for r in ok if r["config"] == config_name and r.get("gap") is not None]
        errors = sum(1 for r in failed if r["config"] == config_name)
        if values:
            gap_text = f" · gap medio {100 * sum(gaps) / len(gaps):+.1f}% sobre el mejor conocido" if gaps else ""
            print(f"  {config_name}: media {sum(values) / len(values):.2f} · mejor {min(values):.2f}{gap_text} · "
                  f"{len(values)} corridas{f' · {errors} fallidas' if errors else ''}")
        else:
            print(f"  {config_name}: sin resultados{f' · {errors} fallidas' if errors else ''}")
    if failed:
        print(f"Detalle de los fallos en {relative_to_root(session / 'errors.csv')}")


def batch(args):
    instances = find_instances(args.instances, args.pattern)
    config_files = {f"config{n}": resolve(args.configs_dir) / f"config{n}.json" for n in args.configs}
    missing = [name for name, path in config_files.items() if not path.exists()]
    if missing:
        sys.exit(f"No existen las configuraciones: {', '.join(missing)}")

    jobs = []
    for config_name in config_files:
        for instance in instances:
            for run in range(1, args.runs + 1):
                jobs.append({"config": config_name, "instance": instance.stem, "run": run,
                             "seed": args.seed + len(jobs)})

    print(f"{len(config_files)} configuraciones × {len(instances)} instancias × {args.runs} corridas = {len(jobs)} "
          f"ejecuciones con {args.workers} procesos (semillas {args.seed}–{args.seed + len(jobs) - 1})")
    if args.dry_run:
        for instance in instances:
            print(f"  {relative_to_root(instance)}")
        return

    configs = {}
    for config_name, config_path in config_files.items():
        # Configuración usada, con los cambios indicados por argumentos
        with open(config_path, encoding="utf-8") as file:
            configs[config_name] = json.load(file)
        if args.population is not None:
            configs[config_name]["initial_population_size"] = args.population
        if args.max_iter is not None:
            configs[config_name]["max_iter"] = args.max_iter
    session, manifest = create_session(args, configs, instances, jobs)
    print(f"Resultados en {relative_to_root(session)}")
    execute_session(session, manifest, jobs, args)


def resume(args):
    """Continúa un lanzamiento interrumpido: ejecuta solo las corridas que no terminaron."""
    session = resolve(args.resume)
    if not (session / "manifest.json").exists():
        sys.exit(f"No se encontró {relative_to_root(session / 'manifest.json')}")
    with open(session / "manifest.json", encoding="utf-8") as file:
        manifest = json.load(file)

    jobs = [dict(run) for run in manifest["runs"]]
    complete_jobs(session, manifest, jobs)
    previous, pending = [], []
    for job in jobs:
        record = completed_record(session, job)
        (previous if record is not None else pending).append(record or job)

    code = git_info()
    if code["commit"] != manifest["code"].get("commit"):
        print(f"Aviso: el código actual ({(code['commit'] or '?')[:7]}) no es el del lanzamiento "
              f"({(manifest['code'].get('commit') or '?')[:7]}); las corridas nuevas podrían no ser comparables.")
    manifest.setdefault("resumed", []).append({"at": dt.datetime.now().isoformat(timespec="seconds"),
                                               "code": code, "pending": len(pending)})
    manifest["status"] = "running"
    write_json(session / "manifest.json", manifest)
    print(f"Reanudando {relative_to_root(session)}: {len(previous)} corridas terminadas, {len(pending)} pendientes "
          f"con {args.workers} procesos")
    execute_session(session, manifest, pending, args, previous)


# ------------------------- Reproducción -------------------------
def replay(args):
    """Repite exactamente una corrida guardada (misma configuración, instancia y semilla)."""
    run_csv = resolve(args.replay)
    with open(run_csv, encoding="utf-8") as file:
        record = next(csv.DictReader(file))
    if not record.get("seed"):
        sys.exit("La corrida no registra su semilla (formato anterior): no se puede reproducir.")

    session = next((p for p in run_csv.parents if (p / "manifest.json").exists()), None)
    if session is None:
        sys.exit("No se encontró el manifest.json del lanzamiento al que pertenece la corrida.")
    with open(session / "manifest.json", encoding="utf-8") as file:
        manifest = json.load(file)

    config_name, instance_name = record["config"], record["instance"]
    config_path = session / manifest["configs"][config_name]
    instance_path = resolve(manifest["instances"][instance_name])
    code = git_info()
    original_code = manifest["code"]
    if original_code.get("commit") != code["commit"]:
        print(f"Aviso: el código actual ({(code['commit'] or '?')[:7]}) no es el de la corrida original "
              f"({(original_code.get('commit') or '?')[:7]}); el resultado podría diferir.")
    elif code["dirty"] or original_code.get("dirty"):
        print("Aviso: el código tiene cambios sin confirmar (ahora o cuando se ejecutó la corrida original); "
              "el resultado podría diferir.")

    output = new_session_dir(resolve(args.output), "_replay")
    write_json(output / "manifest.json", {
        "started": dt.datetime.now().isoformat(timespec="seconds"), "replay_of": relative_to_root(run_csv),
        "code": code, "python": platform.python_version(), "configs": {config_name: f"configs/{config_name}.json"},
        "instances": {instance_name: relative_to_root(instance_path)},
        "runs": [{"config": config_name, "instance": instance_name, "run": int(record["run"]), "seed": int(record["seed"])}],
    })
    (output / "configs").mkdir()
    shutil.copy(config_path, output / "configs" / f"{config_name}.json")

    logging.basicConfig(level=getattr(logging, args.log_level))
    print(f"Reproduciendo {config_name} · {instance_name} · run {record['run']} (semilla {record['seed']})…")
    result = run_single(config_name, str(output / "configs" / f"{config_name}.json"), str(instance_path),
                        int(record["run"]), int(record["seed"]), str(output), not args.no_images)

    original = float(record["value"]) if record["value"] not in ("", "None") else None
    reproduced = result["value"]
    print(f"Original: {original} · Reproducido: {reproduced} · Resultados en {relative_to_root(output)}")
    if original is not None and reproduced is not None and abs(original - reproduced) < 1e-9:
        print("✓ Resultado idéntico al original")
    else:
        print("✗ El resultado difiere del original")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Ejecución por lotes del algoritmo genético para el SBRP.")
    parser.add_argument("--configs", type=int, nargs="+", default=[7, 8, 9], help="Números de configuración (config<N>.json)")
    parser.add_argument("--configs-dir", default=str(CONFIGS_DIR), help="Carpeta de las configuraciones")
    parser.add_argument("--population", type=int, help="Sustituye el tamaño de población de las configuraciones")
    parser.add_argument("--max-iter", type=int, help="Sustituye el número máximo de generaciones de las configuraciones")
    parser.add_argument("--instances", default="data/instances/real", help="Carpeta de instancias")
    parser.add_argument("--pattern", nargs="+", action="extend",
                        help="Patrones de nombres de instancia, p. ej. 'inst5*' 'inst102-*' (por defecto, todas)")
    parser.add_argument("--runs", type=int, default=1, help="Corridas por configuración e instancia")
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1), help="Procesos en paralelo")
    parser.add_argument("--seed", type=int, default=1, help="Semilla base (cada corrida usa base + índice)")
    parser.add_argument("--output", default="results", help="Carpeta donde se crea la carpeta del lanzamiento")
    parser.add_argument("--log-level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--no-images", action="store_true", help="No guardar la imagen de cada corrida")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar el plan sin ejecutar")
    parser.add_argument("--replay", help="Reproducir exactamente una corrida guardada (ruta a su run_<k>.csv)")
    parser.add_argument("--resume", help="Continuar un lanzamiento interrumpido (ruta a su carpeta); solo ejecuta "
                                         "las corridas que no terminaron")
    return parser.parse_args()


if __name__ == "__main__":
    # La salida usa caracteres no ASCII (×, →, ✓); en Windows, al redirigirla, Python usaría cp1252 y fallaría
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    arguments = parse_args()
    if arguments.replay:
        replay(arguments)
    elif arguments.resume:
        resume(arguments)
    else:
        batch(arguments)
