import numpy as np

def _place_pattern(grid: np.ndarray, pattern: list[list[int]], top: int, left: int) -> None:
    arr = np.array(pattern, dtype=int)
    h, w = arr.shape
    grid[top:top + h, left:left + w] = arr

def create_glider(size: int = 200) -> np.ndarray:
    grid = np.zeros((size, size), dtype=int)
    glider = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    _place_pattern(grid, glider, top=20, left=20)
    return grid

def create_still_life_beehive(size: int = 200) -> np.ndarray:
    grid = np.zeros((size, size), dtype=int)
    beehive = [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
    ]
    for offset in range(40, 160, 35):
        _place_pattern(grid, beehive, top=offset, left=offset)
        _place_pattern(grid, beehive, top=offset, left=size - offset - 4)
    return grid

def create_pulsar_oscillator(size: int = 200) -> np.ndarray:
    grid = np.zeros((size, size), dtype=int)

    quarter = np.zeros((6, 6), dtype=int)
    quarter[0, 2:5] = 1
    quarter[5, 2:5] = 1
    quarter[2:5, 0] = 1
    quarter[2:5, 5] = 1

    full_pulsar = np.zeros((13, 13), dtype=int)
    full_pulsar[0:6, 0:6] = quarter
    full_pulsar[0:6, 7:13] = np.fliplr(quarter)
    full_pulsar[7:13, 0:6] = np.flipud(quarter)
    full_pulsar[7:13, 7:13] = np.flipud(np.fliplr(quarter))

    center = size // 2 - 6
    _place_pattern(grid, full_pulsar.tolist(), top=center, left=center)
    return grid


def create_gosper_glider_gun(size: int = 200) -> np.ndarray:
    grid = np.zeros((size, size), dtype=int)
    gun_coords = [
        (5, 1), (5, 2), (6, 1), (6, 2),
        (5, 11), (6, 11), (7, 11), (4, 12), (8, 12), (3, 13), (9, 13),
        (3, 14), (9, 14), (6, 15), (4, 16), (8, 16), (5, 17), (6, 17),
        (7, 17), (6, 18), (3, 21), (4, 21), (5, 21), (3, 22), (4, 22),
        (5, 22), (2, 23), (6, 23), (1, 25), (2, 25), (6, 25), (7, 25),
        (3, 35), (4, 35), (3, 36), (4, 36),
    ]
    for r, c in gun_coords:
        grid[r + 20, c + 20] = 1
    return grid


def create_winter_bee_cluster(size: int = 200, seed: int = 42) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    grid = np.zeros((size, size), dtype=int)
    temp = np.full((size, size), -8.0, dtype=float)
    energy = np.zeros((size, size), dtype=float)

    # 1.Rectangular honey reserve at the top
    grid[45:75, 65:135] = 3

    # 2.Square bee cluster right below the honey
    grid[75:135, 70:130] = 1
    temp[75:135, 70:130] = 22.0
    temp[85:125, 80:120] = 28.0
    energy[75:135, 70:130] = rng.uniform(55.0, 100.0, size=(60, 60))

    return grid, temp, energy
