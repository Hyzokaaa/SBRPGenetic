# ![SBRPGenetic](docs/logoWatercolor.svg)

## Descripción del Proyecto
SBRPGenetic es una solución al problema de rutas de autobuses escolares (SBRP) utilizando algoritmos genéticos. Este proyecto es parte de una tesis para la Universidad Tecnológica de La Habana CUJAE.

> [ADVERTENCIA]
> Este proyecto está actualmente en desarrollo.

> [NOTA]
> Se aceptan contribuciones al proyecto, especialmente de caracter visual
## Índice
1. Funcionalidades
2. Instalación
3. Uso
4. Contribución
## Funcionalidades
(TODO)

## Instalación
### *Ejecución utilizando `Pycharm`*
1. *Clonar el proyecto*
   1. Ve a `VCS` > `Get from Version Control`.
   2. En el cuadro de diálogo `Get from Version Control`, selecciona `GitHub` en la izquierda.
   3. Pega el enlace `https://github.com/Hyzokaaa/SBRPGenetic.git` en el campo `URL` y elige tu directorio.
   4. Haz clic en el botón `Clone`.

2. *Crear entorno virtual*
   1. Ve a `File` > `Settings` > `Project` > `Python Interpreter`.
   2. Haz clic en el selector del intérprete de Python y elige `Add New Interpreter`.
   3. En el cuadro de diálogo `Add Python Interpreter`, selecciona `Virtualenv Environment`.
   4. Especifica la ubicación del nuevo entorno virtual en el campo `Location`.
   5. Elige el intérprete base de la lista. (`python-3.11`)
   6. Haz clic en `OK` para completar la tarea.

3. *Actualizar las dependencias*
   1. Abre la terminal en PyCharm (`View` > `Tool Windows` > `Terminal`).
   2. Navega al directorio donde se encuentra el archivo `requirements.txt`.
   3. Ejecuta el comando:
   ```bash
    pip install -r requirements.txt
    ```

4. *Ejecutar el archivo principal del proyecto*
   1. Haz clic con el botón derecho en el editor y selecciona `Run 'main'` del menú contextual.
   2. Otra opción es presionar `Control+Shift+F10`.

### *Ejecución utilizando una Terminal*
1. *Clonar el proyecto*
   1. Abre la terminal.
   2. Navega al directorio donde deseas clonar el proyecto.
   3. Ejecuta el comando:
   ```bash
    git clone https://github.com/Hyzokaaa/SBRPGenetic.git
    ```

2. *Crear entorno virtual*
   1. Navega al directorio del proyecto clonado.
   2. Ejecuta el comando:
   ```bash
    python3 -m venv env
    ```
   3. Activa el entorno virtual con:
   ```bash
    source env/bin/activate
    ```

3. *Actualizar las dependencias*
   1. Asegúrate de que el entorno virtual esté activado.
   2. Ejecuta el comando:
   ```bash
    pip install -r requirements.txt
    ```

4. *Ejecutar el archivo principal del proyecto*
   1. Asegúrate de que el entorno virtual esté activado.
   2. Desde la raíz del proyecto, ejecuta el comando (ver «Ejecución por lotes» más abajo):
   ```bash
    python app/main.py --dry-run
    ```


## Uso
### Ejecución por lotes
`app/main.py` ejecuta las configuraciones indicadas sobre un conjunto de instancias, en paralelo:
```bash
python app/main.py --configs 7 8 9 --pattern "inst5*" --runs 3 --workers 4
```
Opciones principales: `--configs` (números de `config<N>.json`), `--instances` (carpeta, por defecto `data/instances/real`),
`--pattern` (uno o varios filtros de nombres, p. ej. `--pattern "inst54-*" "inst102-*"`), `--runs` (corridas por instancia), `--seed` (semilla base), `--population` y `--max-iter`
(sustituyen los valores de las configuraciones), `--dry-run` (muestra el plan sin ejecutar). `python app/main.py --help` las lista todas.

Cada lanzamiento crea `results/<fecha_hora>/` con los resultados (`config<N>/<instancia>/run_<k>.csv` y su imagen),
una copia de las configuraciones usadas, `manifest.json` (argumentos, semillas y versión del código), `run.log`,
`summary.csv` y, si alguna corrida falla, `errors.csv`. Una corrida que falla no detiene el lote.

`summary.csv` incluye el mejor valor conocido de cada instancia (`best_known`) y el `gap` de la corrida respecto a él,
y al terminar se muestra el gap medio de cada configuración. Los mejores conocidos están en
`data/instances/best_known.csv`: óptimos del MIP, cotas inferiores y soluciones GRASP+VND de Schittekat et al. (2013,
*A metaheuristic for the school bus routing problem with bus stop selection*, EJOR 229(2)) y la escalada de la tesis de
Pérez Pérez (2020); la columna `optimal` indica los 59 valores probados óptimos.

Cada corrida usa una semilla registrada, por lo que puede reproducirse exactamente:
```bash
python app/main.py --replay results/<fecha_hora>/config7/<instancia>/run_2.csv
```

Un lanzamiento interrumpido (corte de luz, reinicio) se continúa sin repetir las corridas ya terminadas:
```bash
python app/main.py --resume results/<fecha_hora>
```

### Rejilla de operadores
`app/grid.py` ejecuta todas las combinaciones de asignación, generación de rutas, selección, cruce, mutación,
reemplazo y diversidad partiendo de una configuración base (con `--only` se limitan los factores que no interesan), con el mismo presupuesto para todas (población
y generaciones fijas, sin parada por estancamiento) y la misma semilla para cada instancia y corrida en todas las
combinaciones. Guarda `grid.csv` con los operadores de cada configuración y se reanuda con `--resume`:
```bash
python app/grid.py --pattern "inst27-*" "inst54-*" --runs 2 --workers 14
```
`--only FACTOR=NIVEL[,NIVEL]` limita los niveles de un factor (p. ej. `crossover_operator=BCRC_CROSSOVER_OPERATOR_SBRP`).

### Asignación de estudiantes a paradas
La asignación se decide antes de construir las rutas (`stop_assign_strategy`) y es la decisión que más pesa en la
calidad de las soluciones, sobre todo cuando los estudiantes pueden caminar mucho (`w` grande):
- `H_STUDENT_TO_CLOSEST_STOP_STRATEGY`, `H_STUDENT_TO_STOP_CLOSEST_TO_SCHOOL_STRATEGY`,
  `H_STUDENT_TO_STOP_CLOSEST_TO_CENTROID_STRATEGY` y `STUDENT_TO_RANDOM_STOP_STRATEGY`: cada estudiante va a la parada
  alcanzable más cercana a su casa, a la escuela, al centroide de las paradas o a una al azar.
- `H_STUDENT_TO_FEWEST_STOPS_STRATEGY`: usa el menor número de paradas posible (en cada paso abre la parada que recibe a
  más estudiantes). Su parámetro `school_weight` da preferencia a las paradas cercanas a la escuela.

`stop_assign_portfolio` sustituye a `stop_assign_strategy` por una lista de asignaciones: el algoritmo se ejecuta con
cada una y devuelve la mejor solución, y la columna `assignment` de los resultados indica cuál ganó. Para no gastar más
tiempo, el presupuesto (`max_iter`) se reparte entre ellas, como en `config17`:
```json
"stop_assign_portfolio": [
    "H_STUDENT_TO_STOP_CLOSEST_TO_SCHOOL_STRATEGY",
    {"name": "H_STUDENT_TO_FEWEST_STOPS_STRATEGY", "params": {"school_weight": 3.0}}
]
```

Tras ejecutar el algoritmo, `assignment_improvement_operator` puede mejorar la asignación a partir de las rutas
encontradas: `STOP_REMOVAL_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP` cierra cada parada visitada cuyos estudiantes pueden
caminar a otras paradas visitadas (con reasignaciones en cadena, respetando la distancia a pie y la capacidad), lo que
acorta las rutas sin empeorar nunca la solución. `STOP_REPLACEMENT_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP` cambia una
parada visitada por una no visitada cercana cuando la ruta se acorta y sus estudiantes pueden caminar a las paradas
visitadas, y `COMPOSITE_ASSIGNMENT_IMPROVEMENT_OPERATOR_SBRP` alterna ambas mejoras mientras alguna cambie algo. Con `assignment_rounds` mayor que 1, el algoritmo se vuelve a ejecutar
con la nueva asignación mientras la mejora siga cambiando algo. Dentro de cada ejecución la asignación es fija.

| Configuración | Gap medio sobre el mejor conocido (120 instancias, mejor de 10 semillas) |
|---|---|
| `config14`: mejores operadores de la rejilla, asignación por cercanía a la escuela | +7.6 % |
| `config15`: `config14` con la asignación de mínimas paradas | +4.6 % |
| `config17`: `config14` con un portafolio de 4 asignaciones y el mismo presupuesto | +3.6 % |
| `config18`: `config17` cerrando paradas tras el algoritmo | +2.1 % |
| `config19`: `config18` cerrando y sustituyendo paradas tras el algoritmo (configuración recomendada) | +1.8 % |

### Selección, reemplazo y diversidad
Además del torneo y la ruleta, la selección puede ser aleatoria (`RANDOM_SELECTION_OPERATOR`), un torneo que a veces
elige al azar (`PROBABILISTIC_TOURNAMENT_SELECTION_OPERATOR`, parámetro `random_probability`) o por ranking lineal
(`LINEAR_RANKING_SELECTION_OPERATOR`, parámetro `pressure` entre 1 y 2). Dos familias más controlan la diversidad de la
población; sin indicarlas, el algoritmo se comporta como siempre:
- `replacement_operator`: `GENERATIONAL_REPLACEMENT_OPERATOR` (por defecto: élite + hijos) o
  `DETERMINISTIC_CROWDING_REPLACEMENT_OPERATOR_SBRP` (cada hijo compite con su padre más parecido; se suele combinar con
  la selección aleatoria).
- `diversity_operator`: `NO_DIVERSITY_OPERATOR` (por defecto), `RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR`,
  `TRIGGERED_HYPERMUTATION_DIVERSITY_OPERATOR`, `CATACLYSMIC_RESTART_DIVERSITY_OPERATOR` (actúan tras varias
  generaciones sin mejora) o `CLEARING_DIVERSITY_OPERATOR_SBRP` (sustituye en cada generación las soluciones casi
  idénticas a otra mejor).

Los parámetros se indican como en el resto de operadores:
```json
"diversity_operator": {"name": "RANDOM_IMMIGRANTS_DIVERSITY_OPERATOR", "params": {"stagnation": 5, "fraction": 0.3}}
```

### Algoritmos de referencia
La clave opcional `"algorithm"` de una configuración elige el algoritmo: `GA` (por defecto), `RANDOM_SEARCH`
(búsqueda aleatoria) o `HILL_CLIMBING` (escalada). Las referencias sirven para medir cuánto aporta el algoritmo
genético: usan su mismo presupuesto (población × generaciones evaluaciones) y criterio de estancamiento, y solo
aceptan soluciones factibles. `config10` (búsqueda aleatoria) y `config11` (escalada) parten de `config8`:
```bash
python app/main.py --configs 8 10 11 --runs 5
```

### Informe de resultados
`app/report.py` genera el informe de uno o varios lanzamientos: calidad respecto al mejor valor conocido, comparación
con Schittekat et al. (2013), la tesis de Pérez Pérez (2020), el EDA de 2016 y los óptimos del MIP (con la prueba de
Wilcoxon), resultados por tipo de instancia, nuevos mejores valores conocidos, peores instancias y, si se pasan varios
lanzamientos, la comparación entre configuraciones. Escribe `report.md`, `report.html`, `report.pdf` (con Edge, Chrome
o Chromium; su ruta se puede indicar en `SBRP_BROWSER`), las tablas en CSV y las gráficas en PNG:
```bash
python app/report.py results/<fecha_hora>                         # informe en results/<fecha_hora>/report
python app/report.py results/<lanzamiento_A> results/<lanzamiento_B>   # compara configuraciones
```

### Interfaz (laboratorio del algoritmo genético)
Desde la raíz del proyecto, con las dependencias instaladas:
```bash
streamlit run app/ui/app.py
```
Se abre en `http://localhost:8501` y tiene cinco páginas:
- **Inicio**: mapa de la instancia y asignación de estudiantes a paradas.
- **Ejecutar en vivo**: ejecuta el algoritmo genético con cualquier configuración u operador y muestra, generación
  a generación, la convergencia, la diversidad de la población y el mapa de la mejor solución.
- **Laboratorio de operadores**: aplica un cruce, una mutación o la reparación a dos padres y muestra qué aristas
  hereda el hijo de cada padre, cuánto cambia el coste y qué restricciones se rompen o se corrigen.
- **Comparar configuraciones**: ejecuta en paralelo varias configuraciones con varias semillas y compara sus
  distancias (tabla, diagrama de caja y curvas de convergencia).
- **Resultados guardados**: explora los resultados de `app/main.py` y revalida con el validador actual los
  resultados antiguos, que no registraban la factibilidad.

### Pruebas
Con las dependencias de desarrollo instaladas (`pip install -r requirements-dev.txt`), desde la raíz del proyecto:
```bash
python -m pytest                 # todas las pruebas (menos de un minuto)
python -m pytest -m "not slow"   # sin las lentas (ejecución por lotes e interfaz)
```

## Contribución
(TODO)
