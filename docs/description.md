# Problema de Ruteo de Autobuses Escolares (SBRP)

## Características y restricciones

1. Una sola escuela destino de todos los estudiantes.
2. Todos los estudiantes son homogéneos y ninguno requerirá tratamiento especial.
3. Flota homogénea donde todos los autobuses tienen igual capacidad de trasportación y dicha capacidad es fija.
4. Cada parada debe ser visitada como máximo solo una vez.
5. Cada estudiante debe poder alcanzar la parada a la que fue asignado.
6. En cada ruta, no se debe exceder la capacidad del autobús.
7. Cada parada a la que se asigna algún estudiante, debe ser visitada por las rutas de autobuses una y solo una vez.

## Definiciones de las clases

Hemos definido varias clases para representar los diferentes componentes del problema:

- `School`: Representa la escuela. Tiene atributos para el id, el nombre y las coordenadas (coord_x, coord_y).

- `Stop`: Representa una parada de autobús. Tiene atributos para el id, el nombre, las coordenadas (coord_x, coord_y) y el número de estudiantes asignados a la parada (num_assigned_students).

- `Student`: Representa a un estudiante. Tiene atributos para el id, el nombre, las coordenadas (coord_x, coord_y) y la parada asignada al estudiante (assigned_stop).

- `Route`: Representa una ruta de autobús. Tiene un atributo para el autobús asignado a la ruta.

- `Bus`: Representa un autobús. Tiene un atributo para el id.

## Clase SBRP

Hemos definido una clase `SBRP` que representa una instancia del problema. Esta clase tiene los siguientes atributos:

- `school`: Un objeto `School` que representa la escuela.
- `stops`: Una lista de objetos `Stop` que representan las paradas de autobús.
- `students`: Una lista de objetos `Student` que representan a los estudiantes.
- `routes`: Una lista de objetos `Route` que representan las rutas de los autobuses.
- `max_distance`: La distancia máxima que un estudiante puede estar de una parada.
- `bus_capacity`: La capacidad de los autobuses.
- `stop_cost_matrix`: Una matriz de costos entre las paradas.
- `student_stop_cost_matrix`: Una matriz de costos entre los estudiantes y las paradas.

La clase `SBRP` también tiene varios métodos para leer una instancia del problema desde un archivo, calcular la matriz de costos, y asignar estudiantes a paradas. Los métodos de asignación incluyen:

- `student_to_stop`: Asigna a cada estudiante a la parada más cercana que esté dentro de la distancia máxima y que no exceda la capacidad del autobús.
- `student_to_random_stop`: Asigna a cada estudiante a una parada aleatoria que esté dentro de la distancia máxima y que no exceda la capacidad del autobús.
- `student_to_stop_closest_to_school`: Asigna a cada estudiante a la parada más cercana a la escuela que esté dentro de la distancia máxima y que no exceda la capacidad del autobús.

Además, hemos implementado una función `get_valid_stops` para reutilizar el código que obtiene las paradas válidas para un estudiante dado.




## Métodos para asignar estudiantes a paradas

Se definieron varios métodos para asignar estudiantes a paradas: `student_to_better_stop()`, `student_to_random_stop()`, `student_to_stop_closest_to_school()` y `student_to_stop_closest_to_centroid()`. Estos métodos asignan a cada estudiante a una parada que esté dentro de la distancia máxima que el estudiante puede recorrer, ya sea la parada más cercana, una parada aleatoria, la parada más cercana a la escuela o la parada más cercana a centride definido por el conjunto de paradas que tienen estudiantes.

## Método para leer datos de una instancia desde un archivo

Se definió un método `from_file()` en la clase `SBRP` que lee los datos de una instancia del problema desde un archivo y crea una nueva instancia de `SBRP` a partir de estos datos.

## Clase Utils

Se creó una clase `Utils` con dos métodos estáticos: `calculate_distance()` y `calculate_cost_matrix()`. `calculate_distance()` calcula la distancia euclidiana entre dos conjuntos de coordenadas, y `calculate_cost_matrix()` utiliza este método para calcular una matriz de costos entre dos listas de entidades (que podrían ser estudiantes, paradas, etc.).
