from typing import Callable, List, Optional, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.ticker import Locator

from analysis.utils import (
    get_channel_temperature,
    get_enable_read_current,
    get_enable_write_current,
    import_directory,
)
from plotting.helpers import plot_fill_between_array, set_ber_ticks
from plotting.style import CMAP
from plotting.sweeps import plot_read_sweep

READ_XMIN: int = 400
READ_XMAX: int = 1000
IC0_C3: int = 910


def configure_axis(
    ax: Axes,
    xlabel: str,
    ylabel: str,
    xlim: Optional[Tuple[float, float]] = None,
    ylim: Optional[Tuple[float, float]] = None,
    xlocator: Optional[Locator] = None,
    ylocator: Optional[Locator] = None,
) -> Axes:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    if xlocator:
        ax.xaxis.set_major_locator(xlocator)
    if ylocator:
        ax.yaxis.set_major_locator(ylocator)
    return ax


def plot_sweep(
    ax: Axes,
    dict_list: List[dict],
    value_name: str,
    variable_name: str,
    colorbar_label: Optional[str] = None,
    **kwargs,
) -> Axes:
    colors = CMAP(np.linspace(0, 1, len(dict_list)))
    variable_list: List[float] = []

    for i, data_dict in enumerate(dict_list):
        plot_read_sweep(
            ax,
            data_dict,
            value_name,
            variable_name,
            color=colors[i],
            **kwargs,
        )
        variable_list.append(data_dict[variable_name].flatten()[0] * 1e6)

    if colorbar_label:
        norm = mcolors.Normalize(vmin=min(variable_list), vmax=max(variable_list))
        sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
        cbar.set_label(colorbar_label)

    return ax


def plot_temperature(
    ax: Axes,
    currents: List[float],
    temperatures: List[float],
    colors: Optional[np.ndarray] = None,
    marker_size: int = 5,
) -> Axes:
    colors = CMAP(np.linspace(0, 1, len(currents)))
    ax.plot(currents, temperatures, marker="o", color="black", markersize=4)

    for i, (current, temp) in enumerate(zip(currents, temperatures)):
        ax.plot(
            current,
            temp,
            marker="o",
            markersize=marker_size,
            markeredgecolor="black",
            markerfacecolor=colors[i],
            markeredgewidth=0.2,
        )
    return ax


def preprocess_data(
    dict_list: List[dict],
    current_func: Callable[[dict], float],
    temp_func: Callable[[dict, str], float],
    temp_key: str,
) -> Tuple[List[float], List[float]]:
    currents: List[float] = []
    temperatures: List[float] = []

    for data_dict in dict_list:
        current = current_func(data_dict)
        temperature = temp_func(data_dict, temp_key)
        currents.append(current)
        temperatures.append(temperature)

    return currents, temperatures


if __name__ == "__main__":
    # Import data
    data: List[dict] = import_directory("data")
    enable_read_290_list: List[dict] = import_directory("data/figure2/data_290uA")
    enable_read_300_list: List[dict] = import_directory("data/figure2/data_300uA")
    enable_read_310_list: List[dict] = import_directory("data/figure2/data_310uA")
    data_inverse: List[dict] = import_directory("data/figure2/data_inverse")

    dict_list: List[dict] = [enable_read_290_list, enable_read_300_list, enable_read_310_list][2]
    data_list: List[dict] = import_directory("data/figure2/data_enable_write")
    data_list_subset: List[dict] = [data_list[0], data_list[3], data_list[-6], data_list[-1]]

    # Preprocess data
    enable_read_currents, read_temperatures = preprocess_data(
        dict_list, get_enable_read_current, get_channel_temperature, "read"
    )
    enable_write_currents, write_temperatures = preprocess_data(
        data_list, get_enable_write_current, get_channel_temperature, "write"
    )

    # Plot
    fig, axs = plt.subplots(
        2, 2, figsize=(8.3, 4), constrained_layout=True, width_ratios=[1, 0.25]
    )

    # Enable read sweep
    ax = axs[1, 0]
    plot_sweep(ax, dict_list[::-1], "bit_error_rate", "enable_read_current", marker=".")
    plot_fill_between_array(ax, dict_list[::-1])
    ax.axvline(IC0_C3, color="black", linestyle="--")
    configure_axis(ax, "$I_{\mathrm{read}}$ [$\mu$A]", "BER", xlim=(READ_XMIN, READ_XMAX))
    set_ber_ticks(ax)
    # Enable read temperature
    ax = axs[1, 1]
    plot_temperature(ax, enable_read_currents[::-1], read_temperatures[::-1])
    configure_axis(ax, "$I_{\mathrm{enable}}$ [$\mu$A]", "$T_{\mathrm{read}}$ [K]")

    # Enable write sweep
    ax = axs[0, 0]
    plot_sweep(ax, data_list_subset, "bit_error_rate", "enable_write_current", marker=".")
    plot_fill_between_array(ax, data_list_subset)
    configure_axis(ax, "$I_{\mathrm{read}}$ [$\mu$A]", "BER", xlim=(READ_XMIN, READ_XMAX))
    set_ber_ticks(ax)
    # Enable write temperature
    ax = axs[0, 1]
    plot_temperature(ax, enable_write_currents, write_temperatures)
    configure_axis(ax, "$I_{\mathrm{enable}}$ [$\mu$A]", "$T_{\mathrm{write}}$ [K]")

    plt.show()
