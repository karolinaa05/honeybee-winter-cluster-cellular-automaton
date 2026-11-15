import numpy as np
from data_generator import (
    create_glider,
    create_still_life_beehive,
    create_pulsar_oscillator,
    create_gosper_glider_gun,
    create_winter_bee_cluster,
)
from cellular_automation import CellularAutomaton2D
from visualization import run_visualization


def main():
    GRID_SIZE = 200
    STEPS = 120

    print("=== AUTOMAT KOMÓRKOWY 2D (200x200) ===")
    print("Wybierz tryb symulacji:")
    print("1 - Gra w Życie: Glider (szybowiec)")
    print("2 - Gra w Życie: Niezmienny (Beehive / Ul)")
    print("3 - Gra w Życie: Oscylator Pulsar (48 komórek)")
    print("4 - Gra w Życie: Działo Gospera (duży wzorzec)")
    print("5 - WŁASNA REGUŁA: Zimowanie kłębu pszczół (termoregulacja + rotacja)")

    choice = input("Twój wybór [1-5, domyślnie 5]: ").strip() or "5"

    print("\nWybierz warunek brzegowy:")
    print("1 - Periodyczny (periodic / torus)")
    print("2 - Odbijający (reflective)")
    b_choice = input("Twój wybór [1-2, domyślnie 1]: ").strip() or "1"
    boundary = "periodic" if b_choice == "1" else "reflective"

    print("\nWybierz rodzaj sąsiedztwa:")
    print("1 - Moore'a (8 sąsiadów)")
    print("2 - Von Neumanna (4 sąsiadów)")
    print("3 - Heksagonalne (6 sąsiadów na siatce 2D)")
    n_choice = input("Twój wybór [1-3, domyślnie 3 dla pszczół / 1 dla Gry w Życie]: ").strip()
    if not n_choice:
        neighborhood = "hexagonal" if choice == "5" else "moore"
    else:
        neighborhood = {"1": "moore", "2": "von_neumann", "3": "hexagonal"}.get(n_choice, "moore")

    if choice == "5":
        grid, temp, energy = create_winter_bee_cluster(size=GRID_SIZE)
        initial_honey = int(np.sum(grid == 3))
        automaton = CellularAutomaton2D(
            grid=grid,
            rule_mode="bee_winter",
            boundary=boundary,
            neighborhood=neighborhood,
            temp=temp,
            energy=energy,
            outside_temp=-8.0,
        )
        run_visualization(automaton, steps=STEPS, interval=60)

        bee_mask = (automaton.grid == 1) | (automaton.grid == 2)
        final_temp = automaton.temp[bee_mask].mean() if np.any(bee_mask) else -8.0
        final_honey = int(np.sum(automaton.grid == 3))
        print("\n--- OCENA REZULTATU (ZIMOWANIE PSZCZÓŁ) ---")
        print(f"Temperatura otoczenia: -8.0°C | Śr. temperatura wewnątrz kłębu po {STEPS} krokach: {final_temp:.1f}°C")
        print(f"Zużycie zapasów miodu: {initial_honey - final_honey} komórek (pozostało: {final_honey})")
    else:
        generators = {
            "1": create_glider,
            "2": create_still_life_beehive,
            "3": create_pulsar_oscillator,
            "4": create_gosper_glider_gun,
        }
        grid = generators.get(choice, create_glider)(size=GRID_SIZE)
        automaton = CellularAutomaton2D(
            grid=grid,
            rule_mode="game_of_life",
            boundary=boundary,
            neighborhood=neighborhood,
        )
        run_visualization(automaton, steps=STEPS, interval=50)


if __name__ == "__main__":
    main()