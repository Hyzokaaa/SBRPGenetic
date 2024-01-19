# Proyecto de Solución al Problema de Ruteo de Autobuses Escolares (SBRP) utilizando Algoritmo Genético
## Características y Restricciones
* Una sola escuela destino de todos los estudiantes.
* Todos los estudiantes son homogéneos y ninguno requerirá tratamiento especial.
* Flota homogénea donde todos los autobuses tienen igual capacidad de trasportación y dicha capacidad es fija.
* Cada parada debe ser visitada como máximo solo una vez.
* Cada estudiante debe poder alcanzar la parada a la que fue asignado.
* En cada ruta, no se debe exceder la capacidad del autobús.
* Cada parada a la que se asigna algún estudiante, debe ser visitada por las rutas de autobuses una y solo una vez.
## Definiciones de las clases
### 1. Bus
- **Atributos**:
    - `id`: Identificador del autobús.
- **Métodos**:
    - `__init__(self, id)`: Constructor de la clase.

### 2. Route
- **Atributos**:
    - `bus`: Un objeto Bus asignado a la ruta.
    - `stops`: Una lista de paradas.
- **Métodos**:
    - `__init__(self, bus)`: Constructor de la clase.

### 3. RoutePlanner
- **Métodos**:
    - `generate_route(sbrp)`: Genera una única ruta.
    - `generate_routes(sbrp)`: Genera todas las rutas del SBRP.

### 4. SBRP
- **Atributos**:
    - `school`: Un objeto School que representa la escuela.
    - `stops`: Una lista de objetos Stop que representan las paradas de autobús.
    - `students`: Una lista de objetos Student que representan a los estudiantes.
    - `routes`: Una lista de objetos Route que representan las rutas de los autobuses.
    - `max_distance`: La distancia máxima que un estudiante puede estar de una parada.
    - `bus_capacity`: La capacidad de los autobuses.
    - `stop_cost_matrix`: Una matriz de costos entre las paradas.
    - `student_stop_cost_matrix`: Una matriz de costos entre los estudiantes y las paradas.
- **Métodos**:
    - `__init__(self, school, stops, students, routes, max_distance, bus_capacity, stop_cost_matrix, student_stop_cost_matrix)`: Constructor de la clase.
    - `read_instance(filename)`: Lee una instancia del problema desde un archivo.

### 5. School
- **Atributos**:
    - `name`: Nombre de la escuela.
    - `buses`: Lista de buses.
- **Métodos**:
    - `__init__(self, id, name, coord_x, coord_y)`: Constructor de la clase.

### 6. Stop
- **Atributos**:
    - `id`: Identificador de la parada.
    - `name`: Nombre de la parada.
    - `coord_x`: Coordenada x de la parada.
    - `coord_y`: Coordenada y de la parada.
    - `num_assigned_students`: Número de estudiantes asignados a la parada.
- **Métodos**:
    - `__init__(self, id, name, coord_x, coord_y, num_assigned_students)`: Constructor de la clase.

### 7. StopAssigner
- **Métodos**:
    - `student_to_better_stop(sbrp)`: Asigna a cada estudiante a la parada más cercana que esté dentro de la distancia máxima y que no exceda la capacidad del autobús.
    - `student_to_random_stop(sbrp)`: Asigna a cada estudiante a una parada aleatoria que esté dentro de la distancia máxima y que no exceda la capacidad del autobús.
    - `student_to_stop_closest_to_school(sbrp)`: Asigna a cada estudiante a la parada más cercana a la escuela que esté dentro de la distancia máxima y que no exceda la capacidad del autobús.
    - `get_valid_stops(sbrp, student)`: Obtiene las paradas válidas para un estudiante dado.

### 8. Student
- **Atributos**:
    - `id`: Identificador del estudiante.
    - `name`: Nombre del estudiante.
    - `coord_x`: Coordenada x del estudiante.
    - `coord_y`: Coordenada y del estudiante.
    - `assigned_stop`: Parada asignada al estudiante.
- **Métodos**:
    - `__init__(self, id, name, coord_x, coord_y, assigned_stop)`: Constructor de la clase.

### 9. Utils
- **Métodos**:
    - `calculate_distance(coord1_x, coord1_y, coord2_x, coord2_y)`: Calcula la distancia euclidiana entre dos conjuntos de coordenadas.
    - `calculate_cost_matrix(entities1, entities2)`: Genera la matriz de costo de dos entidades utilizando el método calculate_distance.
    - `calculate_centroid(stops: List[Stop])`: Busca el centroide entre una lista de paradas.

### 10. Visualizer
- **Métodos**:
    - `plot_assignments(sbrp)`: Dibuja el escenario del SBRP con el objetivo de tener una representación gráfica del mismo.

### 11. GeneticAlgorithm
- **Atributos**:
    - `population_size`: Tamaño de la población.
    - `mutation_rate`: Índice de mutation.
    - `crossover_rate`: Índice de cruzamiento.
    - `sbrp`: Instancia del problema particular.
    - `population[]`: Población inicial.
- **Métodos**:
    - `initialize_population()`: Genera la población inicial de soluciones.
    - `calculate_fitness()`: Calcula la calidad de la población de soluciones. Devuelve una lista con la calidad de cada
  solución particular dentro de la población de soluciones.
    - `selection()`: Selecciona a los individuos para la próxima generación.
    - `crossover`: Realiza el cruce entre dos individuos seleccionados.
    - `mutation()`: Aplica una mutación a un individuo seleccionado.
    - `run()`: Ejecuta el algoritmo genético.
