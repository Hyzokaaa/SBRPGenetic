class GeneticAlgorithmConfig:
    def __init__(self):
        self.instance_path = None  # Path to the instance file
        self.problem = None  # Problem object to be solved
        self.data_input = None  # Data input object
        self.distance_operator = None  # Operator for calculating distance
        self.initial_construction_operator = None  # Operator for initial solution construction
        self.selection_operator = None  # Operator for solution selection
        self.crossover_operator = None  # Operator for solution crossover
        self.repair_operator = None  # Operator for solution repair
        self.mutation_operator = None  # Operator for solution mutation
        self.stop_assign_strategy = None  # Strategy for assigning stops
        self.route_generator_strategy = None  # Strategy for generating routes
        self.objective_max = False  # Boolean to indicate if the objective is to maximize
        self.tournament_size = 10  # Tournament size for solution selection
        self.number_of_selected_solutions = 2  # Number of selected solutions
        self.initial_population_size = 100  # Size of the initial population
        self.max_iter = 1000  # Maximum number of iterations
        self.mutation_rate = 0.1  # Mutation rate
        self.crossover_rate = 0.9   # Crossover rate
