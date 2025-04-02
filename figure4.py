import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker

from plotting.sweeps import (
    plot_enable_write_sweep_multiple,
    plot_write_sweep,
)
from plotting.arrays import (
    plot_parameter_array,
)
from analysis.utils import (
    convert_cell_to_coordinates,
    get_bit_error_rate,
    get_bit_error_rate_args,
    get_channel_temperature,
    get_channel_temperature_sweep,
    get_critical_current_heater_off,
    get_enable_current_sweep,
    get_enable_write_current,
    get_read_current,
    get_read_currents,
    get_write_current,
    import_directory,
    initialize_dict,
    process_cell,
)
from cells import CELLS
from plotting.style import CMAP, CMAP2, apply_snm_style

apply_snm_style()


# range set 1 [::2]
def plot_enable_sweep(
    ax: plt.Axes,
    dict_list: list[dict],
    range=None,
    add_errorbar=False,
    show_colorbar=False,
):
    N = len(dict_list)
    if range is not None:
        dict_list = dict_list[range]
    # ax, ax2 = plot_enable_write_sweep_multiple(ax, dict_list[0:6])
    ax = plot_enable_write_sweep_multiple(
        ax, dict_list, N=N, show_colorbar=show_colorbar
    )

    ax.set_ylabel("BER")
    ax.set_xlabel("$I_{\mathrm{enable}}$ [$\mu$A]")
    return ax


def plot_enable_sweep_markers(ax: plt.Axes, dict_list: list[dict]):
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.20))
    ax.set_ylim([8.3, 9.7])
    N=4
    write_temp_array = np.empty((len(dict_list), N))
    write_current_array = np.empty((len(dict_list), 1))
    enable_current_array = np.empty((len(dict_list), N))
    for j, data_dict in enumerate(dict_list):
        bit_error_rate = get_bit_error_rate(data_dict)
        berargs = get_bit_error_rate_args(bit_error_rate)
        write_current = get_write_current(data_dict)
        write_temps = get_channel_temperature_sweep(data_dict)
        enable_currents = get_enable_current_sweep(data_dict)
        write_current_array[j] = write_current
        critical_current_zero = get_critical_current_heater_off(data_dict)
        for i, arg in enumerate(berargs):
            if arg is not np.nan:
                write_temp_array[j, i] = write_temps[arg]
                enable_current_array[j, i] = enable_currents[arg]
    markers = ["o", "s", "D", "^"]
    colors = CMAP(np.linspace(0, 1, N))
    for i in range(N):
        ax.plot(
            enable_current_array[:, i],
            write_current_array,
            linestyle="--",
            marker=markers[i],
            markeredgecolor="k",
            markeredgewidth=0.5,
            color=colors[i],
        )
    ax.set_ylim(0, 100)
    ax.set_xlim(250, 340)
    ax.yaxis.set_major_locator(plt.MultipleLocator(20))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(10))
    ax.xaxis.set_major_locator(plt.MultipleLocator(25))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(5))
    ax.grid()
    ax.set_ylabel("$I_{\mathrm{write}}$ [$\mu$A]")
    ax.set_xlabel("$I_{\mathrm{enable}}$ [$\mu$A]")
    ax.legend(
        [
            "$I_{1}$",
            "$I_{0}$",
            "$I_{0,\mathrm{inv}}$",
            "$I_{1,\mathrm{inv}}$",
        ],
        loc="lower left",
        frameon=True,
        ncol=1,
        facecolor="white",
        edgecolor="none",
    )


def plot_write_sweep_formatted(ax: plt.Axes, dict_list: list[dict]):
    plot_write_sweep(ax, dict_list)
    ax.set_xlabel("$I_{\mathrm{write}}$ [$\mu$A]")
    ax.set_ylabel("BER")
    ax.set_xlim(0, 300)
    return ax


def plot_write_sweep_formatted_markers(ax: plt.Axes, data_dict: dict):
    data = data_dict.get("data")
    data2 = data_dict.get("data2")
    colors = CMAP2(np.linspace(0, 1, 4))
    ax.plot(
        [d["write_current"] for d in data],
        [d["write_temp"] for d in data],
        "d",
        color=colors[0],
        markeredgecolor="black",
        markeredgewidth=0.5,
    )
    ax.plot(
        [d["write_current"] for d in data2],
        [d["write_temp"] for d in data2],
        "o",
        color=colors[2],
        markeredgecolor="black",
        markeredgewidth=0.5,
    )
    ax.set_xlabel("$I_{\mathrm{write}}$ [$\mu$A]")
    ax.set_ylabel("$T_{\mathrm{write}}$ [K]")
    ax.set_xlim(0, 300)
    ax.legend(
        ["Lower bound", "Upper bound"],
        loc="upper right",
        fontsize=6,
        facecolor="white",
        frameon=True,
    )
    ax.grid()
    return ax


def plot_delay(ax: plt.Axes, data_dict: dict):
    delay_list = data_dict.get("delay")
    bit_error_rate = data_dict.get("bit_error_rate")
    N = 200e3
    sort_index = np.argsort(delay_list)
    delay_list = np.array(delay_list)[sort_index]
    bit_error_rate = np.array(bit_error_rate)[sort_index]
    bit_error_rate = np.array(bit_error_rate).flatten()
    ber_std = np.sqrt(bit_error_rate * (1 - bit_error_rate) / N)
    ax.errorbar(
        delay_list,
        bit_error_rate,
        yerr=ber_std,
        fmt="-",
        marker=".",
        color="black",
    )
    ax.set_ylabel("BER")
    ax.set_xlabel("Memory Retention Time (s)")

    ax.set_xscale("log")
    ax.set_xbound(lower=1e-6)
    ax.grid(True, which="both", linestyle="--")

    ax.set_yscale("log")
    ax.set_ylim([1e-4, 1e-3])
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())


def plot_ber_grid(ax: plt.Axes):
    ARRAY_SIZE = (4, 4)
    param_dict = initialize_dict(ARRAY_SIZE)
    xloc_list = []
    yloc_list = []
    for c in CELLS:
        xloc, yloc = convert_cell_to_coordinates(c)
        param_dict = process_cell(CELLS[c], param_dict, xloc, yloc)
        xloc_list.append(xloc)
        yloc_list.append(yloc)

    plot_parameter_array(
        ax,
        xloc_list,
        yloc_list,
        param_dict["bit_error_rate"],
        log=True,
        cmap=plt.get_cmap("Blues").reversed(),
    )

    ax.xaxis.set_label_position("bottom")
    ax.xaxis.set_ticks_position("bottom")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    cax = ax.inset_axes([1.10, 0, 0.1, 1])
    cbar = fig.colorbar(
        ax.get_children()[0], cax=cax, orientation="vertical", label="minimum BER"
    )

    return ax


def import_write_sweep_formatted() -> list[dict]:
    dict_list = import_directory("data/figure4/data2")

    dict_list = dict_list[1:]
    dict_list = dict_list[::-1]
    dict_list = sorted(
        dict_list, key=lambda x: x.get("enable_write_current").flatten()[0]
    )
    return dict_list


def import_delay_dict() -> dict:
    dict_list = import_directory(
        os.path.join(os.path.dirname(__file__), "data/figure4/data3")
    )
    delay_list = []
    bit_error_rate_list = []
    for data_dict in dict_list:
        delay = data_dict.get("delay").flatten()[0] * 1e-3
        bit_error_rate = get_bit_error_rate(data_dict)

        delay_list.append(delay)
        bit_error_rate_list.append(bit_error_rate)

    delay_dict = {}
    delay_dict["delay"] = delay_list
    delay_dict["bit_error_rate"] = bit_error_rate_list
    return delay_dict


def import_write_sweep_formatted_markers(dict_list) -> list[dict]:
    data = []
    data2 = []
    for data_dict in dict_list:
        bit_error_rate = get_bit_error_rate(data_dict)
        berargs = get_bit_error_rate_args(bit_error_rate)
        write_currents = get_read_currents(
            data_dict
        )  # This is correct. "y" is the write current in this .mat.
        enable_write_current = get_enable_write_current(data_dict)
        read_current = get_read_current(data_dict)
        write_current = get_write_current(data_dict)

        for i, arg in enumerate(berargs):
            if arg is not np.nan:

                if i == 0:
                    data.append(
                        {
                            "write_current": write_currents[arg],
                            "write_temp": get_channel_temperature(data_dict, "write"),
                            "read_current": read_current,
                            "enable_write_current": enable_write_current,
                        }
                    )
                if i == 2:
                    data2.append(
                        {
                            "write_current": write_currents[arg],
                            "write_temp": get_channel_temperature(data_dict, "write"),
                            "read_current": read_current,
                            "enable_write_current": enable_write_current,
                        }
                    )
    data_dict = {
        "data": data,
        "data2": data2,
    }
    return data_dict


if __name__ == "__main__":
    inner = [
        ["A", "C"],
    ]
    innerb = [
        ["B", "D"],
    ]
    innerc = [
        ["delay", "bergrid"],
    ]
    outer_nested_mosaic = [
        [inner],
        [innerb],
        [innerc],
    ]

    fig, axs = plt.subplot_mosaic(
        outer_nested_mosaic,
        figsize=(180 / 25.4, 180 / 25.4),
    )

    dict_list = import_directory("data/figure4/data")
    sort_dict_list = sorted(
        dict_list, key=lambda x: x.get("write_current").flatten()[0]
    )

    ax = axs["A"]
    plot_enable_sweep(ax, sort_dict_list, range=slice(0, len(sort_dict_list), 2))

    ax = axs["B"]
    plot_enable_sweep_markers(ax, sort_dict_list)

    dict_list = import_write_sweep_formatted()
    plot_write_sweep_formatted(axs["C"], dict_list)

    data_dict = import_write_sweep_formatted_markers(dict_list)
    plot_write_sweep_formatted_markers(axs["D"], data_dict)

    delay_dict = import_delay_dict()

    plot_delay(axs["delay"], delay_dict)

    plot_ber_grid(axs["bergrid"])
    fig.subplots_adjust(wspace=0.4, hspace=0.5)

    axpos = axs["A"].get_position()
    ax2pos = axs["B"].get_position()
    axs["B"].set_position([ax2pos.x0, ax2pos.y0, axpos.width, axpos.height])
    ax3pos = axs["C"].get_position()
    ax4pos = axs["D"].get_position()
    axs["D"].set_position([ax4pos.x0, ax4pos.y0, ax3pos.width, ax3pos.height])
    delay_pos = axs["delay"].get_position()
    axs["delay"].set_position([delay_pos.x0, delay_pos.y0, ax3pos.width, ax3pos.height])
    bergrid_pos = axs["bergrid"].get_position()

    plt.show()
