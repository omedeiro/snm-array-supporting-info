
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from analysis.utils import (
    get_channel_temperature,
    get_enable_read_current,
    import_directory,
)
from plotting.style import add_dict_colorbar, apply_snm_style, set_figsize_wide
from plotting.sweeps import plot_read_sweep_array

apply_snm_style()


def main():
    fig = plt.figure(figsize=set_figsize_wide())
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.5)

    axs = [fig.add_subplot(gs[i]) for i in range(3)]
    cax = fig.add_subplot(gs[3])  # Dedicated colorbar axis
    dict_list = [
        import_directory("data/sup_figure3/write_current_sweep_C3"),
        import_directory("data/sup_figure3/write_current_sweep_C3_3"),
        import_directory("data/sup_figure3/write_current_sweep_C3_4"),
    ]

    for i, data_dict in enumerate(dict_list):
        enable_temperature = get_channel_temperature(data_dict[0], "read")
        enable_read_current = get_enable_read_current(data_dict[0])
        plot_read_sweep_array(
            axs[i],
            data_dict,
            "bit_error_rate",
            "write_current",
            marker=".",
        )
        axs[i].set_xlabel("Read Current [$\mu$A]")
        axs[i].set_ylabel("Bit Error Rate")
        axs[i].set_title(
            f"$I_{{ER}}$= {enable_read_current} $\mu$A\n"
            f"T= {enable_temperature:.2f} K\n"
        )
        axs[i].set_box_aspect(1.0)
        axs[i].set_xlim(600, 800)

    axpos = axs[2].get_position()
    cbar = add_dict_colorbar(axs[2], dict_list, "write_current", cax=cax)
    cbar.ax.set_position([axpos.x1 + 0.02, axpos.y0, 0.01, axpos.y1 - axpos.y0])

    plt.show()


def plot_read_sweep_import(data_dict: dict[str, list[float]]):
    fig, ax = plt.subplots()
    plot_read_sweep_array(ax, data_dict, "bit_error_rate", "write_current")
    cell = data_dict[0]["cell"][0]

    ax.set_xlabel("Read Current [$\mu$A]")
    ax.set_ylabel("Bit Error Rate")
    ax.legend(
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1, 1),
        title="Write Current [$\mu$A]",
    )
    ax.set_title(f"Cell {cell}")
    return fig, ax


if __name__ == "__main__":
    main()
