import numpy as np


class CellularAutomaton2D:

    def __init__(
            self,
            grid: np.ndarray,
            rule_mode: str = "game_of_life",
            boundary: str = "periodic",
            neighborhood: str = "moore",
            temp: np.ndarray | None = None,
            energy: np.ndarray | None = None,
            outside_temp: float = -8.0,
    ):
        self.grid = grid.copy()
        self.rule_mode = rule_mode
        self.boundary = boundary
        self.neighborhood = neighborhood
        self.outside_temp = outside_temp

        #HoneyBee model
        self.temp = temp.copy() if temp is not None else np.zeros_like(grid, dtype=float)
        self.energy = energy.copy() if energy is not None else np.zeros_like(grid, dtype=float)
        self.iteration = 0

        def _pad_array(self, arr: np.ndarray):


        def _sum_neighbors(self, binary_or_float_grid: np.ndarray):


        def step_game_of_life(self):


        def step_bee_winter_cluster(self):

        def step(self):