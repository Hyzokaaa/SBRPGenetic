import pandas as pd

# Definir los posibles escenarios
scenarios = {
    "stop_assign_strategy": ["STUDENT_TO_RANDOM_STOP_STRATEGY", "STUDENT_TO_CLOSEST_STOP_STRATEGY"],
    "route_generator_strategy": ["RANDOM_ROUTE_GENERATION_STRATEGY", "DETERMINISTIC_ROUTE_GENERATION_STRATEGY"],
    "selection_operator": ["TOURNAMENT_SELECTION_OPERATOR", "ROULETTE_WHEEL_SELECTION_OPERATOR"],
    "crossover_operator": ["UNIFORM_CROSSOVER_OPERATOR", "ONE_POINT_CROSSOVER_OPERATOR"],
    "mutation_operator": ["SWAP_MUTATION_OPERATOR_SBRP", "INVERSION_MUTATION_OPERATOR_SBRP"]
}

# Crear un DataFrame con los escenarios
df_scenarios = pd.DataFrame(scenarios)

# Generar una matriz de valores (ejemplo con valores aleatorios)
import numpy as np
values_matrix = np.random.rand(len(df_scenarios), len(df_scenarios.columns))

# Crear un DataFrame para la matriz de valores
df_values = pd.DataFrame(values_matrix, columns=df_scenarios.columns)

# Mostrar las tablas
print("Escenarios:")
print(df_scenarios)
print("\nMatriz de Valores:")
print(df_values)