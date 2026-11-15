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

        # HoneyBee model
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
            total[0::2] += nw[0::2] + sw[0::2]  # wiersze parzyste
            total[1::2] += ne[1::2] + se[1::2]  # wiersze nieparzyste
            return total

        raise ValueError(f"Nieznany typ sąsiedztwa: {self.neighborhood}")

    def step_game_of_life(self) -> None:
        neighbors = self._sum_neighbors((self.grid == 1).astype(int))
        new_grid = np.zeros_like(self.grid)

        # Rule 1: A dead cell with exactly 3 neighbors becomes alive
        born = (self.grid == 0) & (neighbors == 3)
        # Rule 2: A live cell with 2 or 3 neighbors survives
        # Rules 3 and 4: Fewer than 2 or more than 3 neighbors -> dies
        survive = (self.grid == 1) & ((neighbors == 2) | (neighbors == 3))

        new_grid[born | survive] = 1
        self.grid = new_grid

    def step_bee_winter_cluster(self) -> None:
        bee_mask = (self.grid == 1) | (self.grid == 2)
        neighbor_count = 4.0 if self.neighborhood == "von_neumann" else (
            6.0 if self.neighborhood == "hexagonal" else 8.0
        )

        # 1. Heat diffusion and cluster insulation
        avg_neighbor_temp = self._sum_neighbors(self.temp) / neighbor_count
        bee_neighbors = self._sum_neighbors(bee_mask.astype(float))

        insulation = np.where(bee_neighbors >= (neighbor_count - 1), 0.35, 1.0)
        new_temp = self.temp + 0.22 * insulation * (avg_neighbor_temp - self.temp)

        empty_or_honey = ~bee_mask
        new_temp[empty_or_honey] += 0.30 * (self.outside_temp - new_temp[empty_or_honey])

        # 2. Thermogenesis and energy consumption
        new_grid = self.grid.copy()
        new_energy = self.energy.copy()

        cold_bees = bee_mask & (new_temp < 21.0) & (new_energy > 2.0)
        warm_bees = bee_mask & ~cold_bees

        new_grid[cold_bees] = 2
        new_temp[cold_bees] += 3.8
        new_energy[cold_bees] -= 1.4

        heating_neighbors = self._sum_neighbors(cold_bees.astype(float))
        new_temp[bee_mask] += 0.45 * heating_neighbors[bee_mask]

        new_grid[warm_bees] = 1
        new_energy[warm_bees] = np.maximum(0.0, new_energy[warm_bees] - 0.15)

        # 3. Eating honey
        honey_neighbors = self._sum_neighbors((new_grid == 3).astype(int))
        hungry_near_honey = bee_mask & (new_energy < 60.0) & (honey_neighbors > 0)
        new_energy[hungry_near_honey] = np.minimum(100.0, new_energy[hungry_near_honey] + 35.0)

        hungry_neighbors = self._sum_neighbors(hungry_near_honey.astype(int))
        eaten_honey = (new_grid == 3) & (hungry_neighbors > 0) & (np.random.rand(*new_grid.shape) < 0.35)
        new_grid[eaten_honey] = 0

        # 4. Thermal rotation and upward movement
        shift_up = np.roll(new_grid, shift=-1, axis=0)
        temp_up = np.roll(new_temp, shift=-1, axis=0)
        energy_up = np.roll(new_energy, shift=-1, axis=0)

        can_swap = (
            bee_mask[:-1, :]
            & np.isin(shift_up[:-1, :], [1, 2])
            & (new_temp[:-1, :] > temp_up[:-1, :] + 3.5)
            & (new_energy[:-1, :] > energy_up[:-1, :] + 10.0)
            & (np.random.rand(new_grid.shape[0] - 1, new_grid.shape[1]) < 0.45)
        )
        r_idx, c_idx = np.where(can_swap)
        for r, c in zip(r_idx, c_idx):
            new_grid[r, c], new_grid[r + 1, c] = new_grid[r + 1, c], new_grid[r, c]
            new_energy[r, c], new_energy[r + 1, c] = new_energy[r + 1, c], new_energy[r, c]

        honey_rows = np.where(new_grid == 3)[0]
        if len(honey_rows) > 0:
            target_r = int(honey_rows.mean())
            bee_rows = np.where((new_grid == 1) | (new_grid == 2))[0]
            if len(bee_rows) > 0 and bee_rows.mean() > target_r:
                can_move_up = (
                    ((new_grid[1:, :] == 1) | (new_grid[1:, :] == 2))
                    & (new_grid[:-1, :] == 0)
                    & (np.random.rand(new_grid.shape[0] - 1, new_grid.shape[1]) < 0.08)
                )
                mr, mc = np.where(can_move_up)
                new_grid[mr, mc] = new_grid[mr + 1, mc]
                new_grid[mr + 1, mc] = 0
                new_energy[mr, mc] = new_energy[mr + 1, mc]
                new_energy[mr + 1, mc] = 0.0
                new_temp[mr, mc] = new_temp[mr + 1, mc]

        self.grid = new_grid
        self.temp = np.clip(new_temp, self.outside_temp, 35.0)
        self.energy = new_energy

    def step(self) -> None:
        if self.rule_mode == "game_of_life":
            self.step_game_of_life()
        elif self.rule_mode == "bee_winter":
            self.step_bee_winter_cluster()
        else:
            raise ValueError(f"Nieznany tryb reguł: {self.rule_mode}")
        self.iteration += 1