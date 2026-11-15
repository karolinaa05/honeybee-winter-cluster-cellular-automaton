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

        def _pad_array(self, arr: np.ndarray) -> np.ndarray:
            if self.boundary == "periodic":
                return np.pad(arr, pad_width=1, mode="wrap")
            elif self.boundary == "reflective":
                return np.pad(arr, pad_width=1, mode="reflect")
            else:
                raise ValueError(f"Nieznany warunek brzegowy: {self.boundary}")

        def _sum_neighbors(self, binary_or_float_grid: np.ndarray) -> np.ndarray:
            p = self._pad_array(binary_or_float_grid)

            north = p[:-2, 1:-1]
            south = p[2:, 1:-1]
            west = p[1:-1, :-2]
            east = p[1:-1, 2:]

            if self.neighborhood == "von_neumann":
                return north + south + west + east

            nw = p[:-2, :-2]
            ne = p[:-2, 2:]
            sw = p[2:, :-2]
            se = p[2:, 2:]

            if self.neighborhood == "moore":
                return north + south + west + east + nw + ne + sw + se

            if self.neighborhood == "hexagonal":
                total = north + south + west + east
                total[0::2] += nw[0::2] + sw[0::2]  #wiersze_parzyste
                total[1::2] += ne[1::2] + se[1::2]  #wiersze_nieparzyste
                return total

            raise ValueError(f"Nieznany typ sąsiedztwa: {self.neighborhood}")

        def step_game_of_life(self) -> None:
            neighbors = self._sum_neighbors((self.grid == 1).astype(int))
            new_grid = np.zeros_like(self.grid)

            #Rule 1: A dead cell with exactly 3 neighbors becomes alive
            born = (self.grid == 0) & (neighbors == 3)
            #Rule 2: A live cell with 2 or 3 neighbors survives
            #Rules 3 and 4: Fewer than 2 or more than 3 neighbors -> dies
            survive = (self.grid == 1) & ((neighbors == 2) | (neighbors == 3))

            new_grid[born | survive] = 1
            self.grid = new_grid

        def step_bee_winter_cluster(self):

        def step(self):