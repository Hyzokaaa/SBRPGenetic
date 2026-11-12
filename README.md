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
   2. Ejecuta el comando:
   ```bash
    python main.py
    ```


## Uso
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

## Contribución
(TODO)
