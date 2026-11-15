import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Patch
from cellular_automation import CellularAutomaton2D


def run_visualization(
    automaton: CellularAutomaton2D,
    steps: int = 120,
    interval: int = 60,
    save_gif: bool = False,
    gif_name: str = "simulation.gif",
) -> None:

    plt.style.use("dark_background")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

    if automaton.rule_mode == "game_of_life":
        cmap = ListedColormap(["#1e1e1e", "#00e676"])
        im1 = ax1.imshow(automaton.grid, cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
        ax1.set_title(
            f"Gra w Życie ({automaton.grid.shape[0]}x{automaton.grid.shape[1]})\n"
            f"Brzeg: {automaton.boundary} | Sąsiedztwo: {automaton.neighborhood}",
            fontsize=11,
        )
        ax1.axis("off")

        alive_history = [int(np.sum(automaton.grid == 1))]
        line, = ax2.plot([0], alive_history, color="#00e676", linewidth=2)
        ax2.set_title("Liczba żywych komórek w czasie", fontsize=11)
        ax2.set_xlabel("Iteracja")
        ax2.set_ylabel("Żywe komórki")
        ax2.set_xlim(0, steps)
        ax2.set_ylim(0, max(50, alive_history[0] * 3))
        ax2.grid(True, alpha=0.25)

        def update(frame):
            automaton.step()
            im1.set_data(automaton.grid)

            alive = int(np.sum(automaton.grid == 1))
            alive_history.append(alive)
            line.set_data(range(len(alive_history)), alive_history)
            if alive >= ax2.get_ylim()[1] * 0.9:
                ax2.set_ylim(0, alive * 1.3)

            fig.suptitle(f"Iteracja: {automaton.iteration} / {steps} | Żywe komórki: {alive}", fontsize=13)
            return im1, line

    else:
        bee_cmap = ListedColormap(["#1b1b1b", "#f4b400", "#ff3d00", "#fff59d"])
        im1 = ax1.imshow(automaton.grid, cmap=bee_cmap, vmin=0, vmax=3, interpolation="nearest")
        ax1.set_title(
            f"Kłąb zimowy pszczół ({automaton.grid.shape[0]}x{automaton.grid.shape[1]})\n"
            f"Brzeg: {automaton.boundary} | Sąsiedztwo: {automaton.neighborhood}",
            fontsize=11,
        )
        ax1.axis("off")

        legend_items = [
            Patch(facecolor="#f4b400", label="Pszczoła (izolacja)"),
            Patch(facecolor="#ff3d00", label="Pszczoła (grzanie)"),
            Patch(facecolor="#fff59d", label="Miód (zapas)"),
            Patch(facecolor="#1b1b1b", edgecolor="#555", label="Puste powietrze"),
        ]
        ax1.legend(handles=legend_items, loc="lower center", ncol=2, fontsize=8, framealpha=0.8)

        im2 = ax2.imshow(
            automaton.temp,
            cmap="inferno",
            vmin=automaton.outside_temp,
            vmax=35.0,
            interpolation="nearest",
        )
        ax2.set_title("Rozkład temperatury w kłębie (°C)", fontsize=11)
        ax2.axis("off")
        cbar = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
        cbar.set_label("Temperatura [°C]")

        def update(frame):
            automaton.step()
            im1.set_data(automaton.grid)
            im2.set_data(automaton.temp)

            bee_mask = (automaton.grid == 1) | (automaton.grid == 2)
            avg_t = automaton.temp[bee_mask].mean() if np.any(bee_mask) else automaton.outside_temp
            honey_left = int(np.sum(automaton.grid == 3))
            fig.suptitle(
                f"Iteracja: {automaton.iteration} / {steps} | "
                f"Śr. temp. kłębu: {avg_t:.1f}°C | Komórki miodu: {honey_left}",
                fontsize=12,
            )
            return im1, im2

    ani = FuncAnimation(fig, update, frames=steps, interval=interval, blit=False, repeat=False)
    plt.tight_layout()

    if save_gif:
        ani.save(gif_name, writer="pillow", fps=15)
        print(f"Zapisano animację do pliku: {gif_name}")

    plt.show()