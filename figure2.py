import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import matplotlib.colors as mcolors
import numpy as np

from analysis.utils import (
    CMAP,
    get_channel_temperature,
    get_enable_read_current,
    get_enable_write_current,
    import_directory,
)
from analysis.plotting import (
    plot_read_sweep,
    plot_fill_between,
)

READ_XMIN = 400
READ_XMAX = 1000
IC0_C3 = 910


def plot_enable_write_sweep(ax: plt.Axes, dict_list: list[dict], **kwargs):
    colors = CMAP(np.linspace(0, 1, len(dict_list)))

    for j, data_dict in enumerate(dict_list):
        plot_read_sweep(
            ax, data_dict, "bit_error_rate", "enable_write_current", color=colors[j], **kwargs
        )
        plot_fill_between(ax, data_dict, fill_color=colors[j])

    ax.set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]")
    ax.set_ylabel("BER")
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.set_xlim(READ_XMIN, READ_XMAX)
    ax.xaxis.set_major_locator(plt.MultipleLocator(100))
    return ax


def plot_enable_write_temp(ax: plt.Axes, enable_write_currents, write_temperatures, colors=None):
    colors = CMAP(np.linspace(0, 1, len(enable_write_currents)))
    ax.plot(
        enable_write_currents,
        write_temperatures,
        marker="o",
        color="black",
    )
    for i, idx in enumerate([0, 3, -6, -1]):
        ax.plot(
            enable_write_currents[idx],
            write_temperatures[idx],
            marker="o",
            markersize=6,
            markeredgecolor="black",
            markerfacecolor=colors[idx],
            markeredgewidth=0.2,
        )
    ax.set_xlabel("$I_{\mathrm{enable}}$ [$\mu$A]")
    ax.set_ylabel("$T_{\mathrm{write}}$ [K]")
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.2))
    return ax


def plot_fill_between_array(ax: Axes, dict_list: list[dict]) -> Axes:
    colors = CMAP(np.linspace(0.1, 1, len(dict_list)))
    for i, data_dict in enumerate(dict_list):
        plot_fill_between(ax, data_dict, colors[i])
    return ax


def plot_read_sweep_array(
    ax: Axes,
    dict_list: list[dict],
    value_name: str,
    variable_name: str,
    colorbar=None,
    add_errorbar=False,
    **kwargs,
) -> Axes:
    colors = CMAP(np.linspace(0, 1, len(dict_list)))
    variable_list = []
    for i, data_dict in enumerate(dict_list):
        plot_read_sweep(
            ax,
            data_dict,
            value_name,
            variable_name,
            color=colors[i],
            add_errorbar=add_errorbar,
            **kwargs,
        )
        variable_list.append(data_dict[variable_name].flatten()[0] * 1e6)

    if colorbar is not None:
        norm = mcolors.Normalize(
            vmin=min(variable_list), vmax=max(variable_list)
        )  # Normalize for colormap
        sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
        cbar.set_label("Write Current [$\mu$A]")

    return ax



def plot_enable_read_sweep(ax: plt.Axes, dict_list, **kwargs):
    plot_read_sweep_array(ax, dict_list, "bit_error_rate", "enable_read_current", **kwargs)
    plot_fill_between_array(ax, dict_list)
    ax.axvline(IC0_C3, color="black", linestyle="--")
    ax.set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]")
    ax.set_ylabel("BER")
    ax.set_xlim(READ_XMIN, READ_XMAX)
    return ax


def plot_enable_read_temp(ax: plt.Axes, enable_read_currents, read_temperatures):
    colors = CMAP(np.linspace(0, 1, len(enable_read_currents)))
    ax.plot(
        enable_read_currents,
        read_temperatures,
        marker="o",
        color="black",
        markersize=4,
    )
    enable_read_currents = enable_read_currents[::-1]
    read_temperatures = read_temperatures[::-1]
    for i in range(len(read_temperatures)):
        ax.plot(
            enable_read_currents[i],
            read_temperatures[i],
            marker="o",
            markersize=5,
            markeredgecolor="black",
            markerfacecolor=colors[i],
            markeredgewidth=0.2,
        )

    ax.set_xlabel("$I_{\mathrm{enable}}$ [$\mu$A]")
    ax.set_ylabel("$T_{\mathrm{read}}$ [K]")
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.2))


if __name__ == "__main__":
    # Import
    data = import_directory("data")
    enable_read_290_list = import_directory("data/figure2/data_290uA")
    enable_read_300_list = import_directory("data/figure2/data_300uA")
    enable_read_310_list = import_directory("data/figure2/data_310uA")

    data_inverse = import_directory("data/figure2/data_inverse")

    dict_list = [enable_read_290_list, enable_read_300_list, enable_read_310_list]
    dict_list = dict_list[2]

    data_list = import_directory("data/figure2/data_enable_write")
    data_list2 = [data_list[0], data_list[3], data_list[-6], data_list[-1]]
    colors = CMAP(np.linspace(0, 1, len(data_list2)))

    # Preprocess
    read_temperatures = []
    enable_read_currents = []
    for data_dict in dict_list:
        read_temperature = get_channel_temperature(data_dict, "read")
        enable_read_current = get_enable_read_current(data_dict)
        read_temperatures.append(read_temperature)
        enable_read_currents.append(enable_read_current)

    enable_write_currents = []
    write_temperatures = []
    for i, data_dict in enumerate(data_list):
        enable_write_current = get_enable_write_current(data_dict)
        write_temperature = get_channel_temperature(data_dict, "write")
        enable_write_currents.append(enable_write_current)
        write_temperatures.append(write_temperature)

    # Plot
    fig, axs = plt.subplots(
        2, 2, figsize=(8.3, 4), constrained_layout=True, width_ratios=[1, 0.25]
    )

    ax: plt.Axes = axs[1, 0]
    plot_enable_read_sweep(ax, dict_list[::-1], marker='.')

    ax: plt.Axes = axs[1, 1]
    plot_enable_read_temp(ax, enable_read_currents, read_temperatures)

    ax = axs[0, 0]
    plot_enable_write_sweep(ax, data_list2, marker=".")

    ax = axs[0, 1]
    plot_enable_write_temp(ax, enable_write_currents, write_temperatures)
    plt.show()