import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from typing import Literal
from nmem.analysis.analysis import (
    import_directory,
    plot_read_sweep_array,
    get_channel_temperature,
    get_enable_read_current,
    CMAP3,
)


def add_colorbar(
    ax: plt.Axes,
    data_dict_list: list[dict],
    cbar_label: Literal["write_current", "enable_read_current"],
    cax=None,
):
    data_list = []
    for data_dict in data_dict_list:
        if cbar_label == "write_current":
            data_list += [d["write_current"] * 1e6 for d in data_dict]
            label = "Write Current [$\mu$A]"
        elif cbar_label == "enable_read_current":
            enable_read_current = [get_enable_read_current(d) for d in data_dict]
            # print(f"Enable Read Current: {enable_read_current}")
            # data_list += [enable_read_current]
            data_list = enable_read_current
            label = "Enable Read Current [$\mu$A]"

    norm = mcolors.Normalize(vmin=min(data_list), vmax=max(data_list))
    sm = plt.cm.ScalarMappable(cmap=CMAP3, norm=norm)
    sm.set_array([])

    if cax is not None:
        cbar = plt.colorbar(sm, cax=cax)
    else:
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)

    cbar.set_label(label)
    return cbar


def plot_read_temp_sweep_C3(save=True):
    fig, axs = plt.subplots(2, 2, figsize=(12, 6))
    dict_list = [
        import_directory("write_current_sweep_C3"),
        import_directory("write_current_sweep_C3_4"),
        import_directory("write_current_sweep_C3_3"),
        # import_directory("write_current_sweep_C3_1"),
    ]
    for i, data_dict in enumerate(dict_list):
        enable_temperature = get_channel_temperature(data_dict[0], "read")
        enable_read_current = get_enable_read_current(data_dict[0])
        plot_read_sweep_array(
            axs[i // 2, i % 2],
            data_dict,
            "bit_error_rate",
            "write_current",
            marker=".",
        )
        axs[i // 2, i % 2].set_xlabel("Read Current [$\mu$A]")
        axs[i // 2, i % 2].set_ylabel("Bit Error Rate")
        axs[i // 2, i % 2].set_title(
            f"Enable Read Current: {enable_read_current} $\mu$A, T= {enable_temperature:.2f} K"
        )

    axs[0, 1].legend(
        frameon=False,
        bbox_to_anchor=(1.1, 1),
        loc="upper left",
        title="Write Current [$\mu$A]",
    )
    fig.subplots_adjust(hspace=0.5, wspace=0.3)

    if save:
        plt.savefig("read_current_sweep_write_current_C3.pdf", bbox_inches="tight")


def plot_read_temp_sweep_C3_v2(save=True):
    fig = plt.figure(figsize=(180 / 25.4, 90 / 25.4))
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.5)

    axs = [fig.add_subplot(gs[i]) for i in range(3)]
    cax = fig.add_subplot(gs[3])  # dedicated colorbar axis
    dict_list = [
        import_directory("write_current_sweep_C3"),
        import_directory("write_current_sweep_C3_4"),
        import_directory("write_current_sweep_C3_3"),
        # import_directory("write_current_sweep_C3_1"),
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
            f"Enable Read Current: {enable_read_current} $\mu$A\n"
            f"T= {enable_temperature:.2f} K\n"
        )
        axs[i].set_box_aspect(1.0)
        axs[i].set_xlim(600, 800)
    # axs[i].legend(
    #     frameon=False,
    #     bbox_to_anchor=(1.1, 1.2),
    #     loc="upper left",
    #     title="Write Current [$\mu$A]",
    # )
    axpos = axs[2].get_position()
    cbar = add_colorbar(axs[2], dict_list, "Write current [$\mu$A]", cax=cax)
    cbar.ax.set_position([axpos.x1 + 0.02, axpos.y0, 0.01, axpos.y1 - axpos.y0])
    if save:
        plt.savefig("read_current_sweep_write_current_C3_v2.pdf", bbox_inches="tight")


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
    # plot_read_sweep_import(import_directory("write_current_sweep_B2_0"))
    # plot_read_sweep_import(import_directory("write_current_sweep_B2_1"))
    # plot_read_sweep_import(import_directory("write_current_sweep_B2_2"))

    # plot_read_sweep_import(import_directory("write_current_sweep_A2"))
    # plot_read_sweep_import(import_directory("write_current_sweep_C2"))

    plot_read_temp_sweep_C3_v2()
