import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Patch, Rectangle
from cellular_automation import CellularAutomaton2D


def _apply_hive_theme(fig, ax1, ax2) -> None:
    fig.patch.set_facecolor("#FAF3E0")
    for ax in (ax1, ax2):
        ax.set_facecolor("#FFFDF7")
        ax.tick_params(colors="#3E2723")
        ax.xaxis.label.set_color("#3E2723")
        ax.yaxis.label.set_color("#3E2723")
        ax.title.set_color("#3E2723")
        for spine in ax.spines.values():
            spine.set_edgecolor("#8D6E63")
            spine.set_linewidth(1.5)


def _draw_beehive_frame(ax, grid_size: int) -> None:
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#5D4037")
        spine.set_linewidth(6)

    top_bar = Rectangle((45, 38), grid_size - 90, 6, facecolor="#6D4C41", edgecolor="#3E2723", linewidth=1)
    left_bar = Rectangle((48, 44), 4, grid_size - 75, facecolor="#8D6E63", edgecolor="#5D4037", linewidth=0.8)
    right_bar = Rectangle((grid_size - 52, 44), 4, grid_size - 75, facecolor="#8D6E63", edgecolor="#5D4037", linewidth=0.8)
    ax.add_patch(top_bar)
    ax.add_patch(left_bar)
    ax.add_patch(right_bar)


def run_visualization(
    automaton: CellularAutomaton2D,
    steps: int = 120,
    interval: int = 60,
    save_gif: bool = False,
    gif_name: str = "simulation.gif",
):
    plt.rcdefaults()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.2))
    _apply_hive_theme(fig, ax1, ax2)
    gif_frames = []

    def capture_frame(frame_idx: int) -> None:
        if not save_gif:
            return
        from PIL import Image
        if frame_idx % 2 == 1:
            fig.canvas.draw()
            rgba = np.asarray(fig.canvas.buffer_rgba())
            gif_frames.append(Image.fromarray(rgba).convert("RGB"))
        if frame_idx == steps - 1 and gif_frames:
            gif_frames[0].save(
                gif_name,
                save_all=True,
                append_images=gif_frames[1:],
                duration=interval * 2,
                loop=0,
            )
            print(f"Zapisano animację do pliku: {gif_name}")

    if automaton.rule_mode == "game_of_life":
        cmap = ListedColormap(["#F2E6D0", "#5D4037"])
        im1 = ax1.imshow(automaton.grid, cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
        ax1.set_title(
            f"Gra w Życie ({automaton.grid.shape[0]}x{automaton.grid.shape[1]})\n"
            f"Brzeg: {automaton.boundary} | Sąsiedztwo: {automaton.neighborhood}",
            fontsize=11,
            fontweight="bold",
        )
        ax1.set_xticks([])
        ax1.set_yticks([])

        alive_history = [int(np.sum(automaton.grid == 1))]
        line, = ax2.plot([0], alive_history, color="#6D4C41", linewidth=2.2)
        ax2.set_title("Liczba żywych komórek w czasie", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Iteracja")
        ax2.set_ylabel("Żywe komórki")
        ax2.set_xlim(0, steps)
        ax2.set_ylim(0, max(50, alive_history[0] * 3))
        ax2.grid(True, color="#D7CCC8", linestyle="--", alpha=0.7)

        def update(frame):
            automaton.step()
            im1.set_data(automaton.grid)

            alive = int(np.sum(automaton.grid == 1))
            alive_history.append(alive)
            line.set_data(range(len(alive_history)), alive_history)
            if alive >= ax2.get_ylim()[1] * 0.9:
                ax2.set_ylim(0, alive * 1.3)

            fig.suptitle(
                f"Iteracja: {automaton.iteration} / {steps} | Żywe komórki: {alive}",
                fontsize=13,
                fontweight="bold",
                color="#3E2723",
            )
            capture_frame(frame)
            return im1, line

    else:
        # Beehive palette: 0 = warm wax air, 1 = yellow bee, 2 = heating bee, 3 = amber honey
        bee_cmap = ListedColormap(["#F2E6D0", "#FFD54F", "#D84315", "#B86B00"])
        im1 = ax1.imshow(automaton.grid, cmap=bee_cmap, vmin=0, vmax=3, interpolation="nearest")
        _draw_beehive_frame(ax1, automaton.grid.shape[0])

        ax1.set_title(
            f"Ul — zimowanie kłębu pszczół ({automaton.grid.shape[0]}x{automaton.grid.shape[1]})\n"
            f"Brzeg: {automaton.boundary} | Sąsiedztwo: {automaton.neighborhood}",
            fontsize=11,
            fontweight="bold",
        )
        ax1.set_xticks([])
        ax1.set_yticks([])

        legend_items = [
            Patch(facecolor="#FFD54F", edgecolor="#8D6E63", label="Pszczoła (izolacja)"),
            Patch(facecolor="#D84315", edgecolor="#8D6E63", label="Pszczoła (grzanie)"),
            Patch(facecolor="#B86B00", edgecolor="#8D6E63", label="Miód (zapas)"),
            Patch(facecolor="#F2E6D0", edgecolor="#8D6E63", label="Wnętrze ula"),
        ]
        leg = ax1.legend(
            handles=legend_items,
            loc="lower center",
            ncol=2,
            fontsize=8.5,
            facecolor="#FFFDF7",
            edgecolor="#8D6E63",
            framealpha=0.95,
        )
        for text in leg.get_texts():
            text.set_color("#3E2723")

        honey_history = [int(np.sum(automaton.grid == 3))]
        heating_history = [int(np.sum(automaton.grid == 2))]

        line_honey, = ax2.plot([0], honey_history, color="#B86B00", linewidth=2.4, label="Komórki miodu")
        line_heat, = ax2.plot([0], heating_history, color="#D84315", linewidth=2.0, label="Grzejące pszczoły")
        ax2.set_title("Zapasy miodu i aktywność grzania w czasie", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Iteracja")
        ax2.set_ylabel("Liczba komórek")
        ax2.set_xlim(0, steps)
        ax2.set_ylim(0, max(honey_history[0], 3600) * 1.1)
        ax2.grid(True, color="#D7CCC8", linestyle="--", alpha=0.7)

        leg2 = ax2.legend(loc="upper right", fontsize=9, facecolor="#FFFDF7", edgecolor="#8D6E63")
        for text in leg2.get_texts():
            text.set_color("#3E2723")

        def update(frame):
            automaton.step()
            im1.set_data(automaton.grid)

            honey_left = int(np.sum(automaton.grid == 3))
            heating_bees = int(np.sum(automaton.grid == 2))
            honey_history.append(honey_left)
            heating_history.append(heating_bees)

            x_vals = range(len(honey_history))
            line_honey.set_data(x_vals, honey_history)
            line_heat.set_data(x_vals, heating_history)

            bee_mask = (automaton.grid == 1) | (automaton.grid == 2)
            avg_t = automaton.temp[bee_mask].mean() if np.any(bee_mask) else automaton.outside_temp
            fig.suptitle(
                f"Iteracja: {automaton.iteration} / {steps} | "
                f"Śr. temp. kłębu: {avg_t:.1f}°C | Miód: {honey_left}",
                fontsize=12.5,
                fontweight="bold",
                color="#3E2723",
            )
            capture_frame(frame)
            return im1, line_honey, line_heat

    ani = FuncAnimation(
        fig, update, frames=steps, interval=interval, blit=False, repeat=False, init_func=lambda: []
    )
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    fig.canvas.mpl_connect("close_event", lambda event: ani.event_source.stop())
    plt.show()
    return ani