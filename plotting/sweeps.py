from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator

from analysis.calculations import (
    filter_plateau,
)
from analysis.cell_utils import (
    convert_cell_to_coordinates,
)
from analysis.constants import (
    IC0_C3,
    READ_XMAX,
    READ_XMIN,
)
from analysis.data_processing import (
    get_bit_error_rate,
    get_channel_temperature,
    get_current_cell,
    get_enable_current_sweep,
    get_enable_read_current,
    get_enable_write_current,
    get_fitting_points,
    get_read_currents,
    get_read_width,
    get_step_parameter,
    get_write_current,
    get_write_width,
)
from plotting.arrays import build_array
from plotting.helpers import (
    plot_fill_between_array,
    set_ber_ticks,
)
from plotting.style import CMAP, CMAP3, add_colorbar, add_errorbar


def plot_read_sweep(
    ax: Axes,
    data_dict: dict,
    value_name: Literal["bit_error_rate", "write_0_read_1", "write_1_read_0"],
    variable_name: Literal[
        "enable_write_current",
        "read_width",
        "write_width",
        "write_current",
        "enable_read_current",
        "enable_write_width",
    ],
    show_errorbar: bool = False,
    **kwargs,
) -> Axes:
    # Map value_name to corresponding data
    value_mapping = {
        "bit_error_rate": get_bit_error_rate(data_dict),
        "write_0_read_1": data_dict.get("write_0_read_1").flatten(),
        "write_1_read_0": data_dict.get("write_1_read_0").flatten(),
    }
    value = value_mapping.get(value_name)
    if value is None:
        raise ValueError(f"Invalid value_name: {value_name}")

    # Map variable_name to corresponding data and label
    variable_mapping = {
        "write_current": (get_write_current(data_dict), "{:.2f}$\mu$A"),
        "enable_write_current": (
            get_enable_write_current(data_dict),
            "{:.2f}$\mu$A, {:.2f}K" if get_channel_temperature(data_dict, "write") else "{:.2f}$\mu$A",
        ),
        "read_width": (get_read_width(data_dict), "{:.2f} pts"),
        "write_width": (get_write_width(data_dict), "{:.2f} pts"),
        "enable_read_current": (
            get_enable_read_current(data_dict),
            "{:.2f}$\mu$A, {:.2f}K",
        ),
    }
    variable, label_format = variable_mapping.get(variable_name, (None, None))
    if variable is None:
        raise ValueError(f"Invalid variable_name: {variable_name}")

    label = label_format.format(variable, get_channel_temperature(data_dict, "read") or 0)

    # Plot the data
    read_currents = get_read_currents(data_dict)
    ax.plot(read_currents, value, label=label, **kwargs)

    # Add error bars if required
    if show_errorbar:
        add_errorbar(ax, read_currents, value)
    
    return ax


def plot_enable_write_sweep_multiple(
    ax: Axes,
    dict_list: list[dict],
    show_colorbar: bool = True,
    show_errorbar: bool = False,
    range: slice = None,
) -> Axes:
    if range is not None:
        dict_list = dict_list[range]
    write_current_list = []

    for data_dict in dict_list:
        write_current = get_write_current(data_dict)
        write_current_list.append(write_current)

    for i, data_dict in enumerate(dict_list):
        write_current_norm = write_current_list[i] / 100
        plot_enable_sweep_single(
            ax, data_dict, show_errorbar=show_errorbar, color=CMAP(write_current_norm)
        )

    if show_colorbar:
        add_colorbar(
            ax,
            write_current_list,
            label="Write Current [$\mu$A]",
            cmap=CMAP,
        )
    set_ber_ticks(ax)
    return ax


def plot_enable_sweep_single(
    ax: Axes,
    data_dict: dict,
    show_errorbar: bool = False,
    **kwargs,
) -> Axes:
    enable_currents = get_enable_current_sweep(data_dict)
    bit_error_rate = get_bit_error_rate(data_dict)
    write_current = get_write_current(data_dict)
    ax.plot(
        enable_currents,
        bit_error_rate,
        label=f"$I_{{W}}$ = {write_current:.1f}$\mu$A",
        **kwargs,
    )
    if show_errorbar:
        add_errorbar(
            ax,
            enable_currents,
            bit_error_rate,
            color=kwargs.get("color", 'k'),
        )
    set_ber_ticks(ax)

    ax.set_xlim(enable_currents[0], enable_currents[-1])
    ax.xaxis.set_major_locator(MultipleLocator(25))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    return ax


def plot_read_sweep_switch_probability(
    ax: Axes,
    data_dict: dict,
    **kwargs,
) -> Axes:
    read_currents = get_read_currents(data_dict)
    _, _, total_switch_probability = build_array(data_dict, "total_switches_norm")
    ax.plot(
        read_currents,
        total_switch_probability,
        **kwargs,
    )
    
    set_ber_ticks(ax)
    return ax


def plot_current_sweep_output(
    ax: plt.Axes,
    data_dict: dict,
    **kwargs,
) -> plt.Axes:
    if len(data_dict) > 1:
        data_dict = data_dict[0]
    sweep_param = get_step_parameter(data_dict)
    sweep_current = data_dict[sweep_param]
    read_zero_voltage = data_dict["read_zero_voltage"]
    read_one_voltage = data_dict["read_one_voltage"]

    base_label = f" {kwargs['label']}" if "label" in kwargs else ""
    kwargs.pop("label", None)
    ax.plot(
        sweep_current,
        read_zero_voltage * 1e3,
        "-o",
        label=f"{base_label} Read 0",
        **kwargs,
    )
    ax.plot(
        sweep_current,
        read_one_voltage * 1e3,
        "--o",
        label=f"{base_label} Read 1",
        **kwargs,
    )
    ax.set_ylabel("Output Voltage (mV)")
    ax.set_xlabel(f"{sweep_param} (uA)")
    ax.legend()
    return ax


def plot_current_sweep_ber(
    ax: plt.Axes,
    data_dict: dict,
    **kwargs,
) -> plt.Axes:
    if len(data_dict) > 1:
        data_dict = data_dict[0]
    sweep_param = get_step_parameter(data_dict)
    sweep_current = data_dict[sweep_param]
    ber = data_dict["bit_error_rate"]

    base_label = f" {kwargs['label']}" if "label" in kwargs else ""
    kwargs.pop("label", None)
    ax.plot(sweep_current, ber, label=f"{base_label}", **kwargs)
    ax.set_xlim(650, 850)
    ax.xaxis.set_major_locator(plt.MultipleLocator(50))

    set_ber_ticks(ax)
    return ax


def plot_current_sweep_switching(
    ax: plt.Axes,
    data_dict: dict,
    **kwargs,
) -> plt.Axes:
    if len(data_dict) > 1:
        data_dict = data_dict[0]
    sweep_param = get_step_parameter(data_dict)
    sweep_current = data_dict[sweep_param]
    switching_probability = data_dict["switching_probability"]

    base_label = f" {kwargs['label']}" if "label" in kwargs else ""
    kwargs.pop("label", None)
    ax.plot(sweep_current, switching_probability, label=f"{base_label}", **kwargs)
    ax.set_xlim(650, 850)
    ax.xaxis.set_major_locator(plt.MultipleLocator(50))

    set_ber_ticks(ax)
    return ax


def plot_current_sweep_persistent(
    ax: plt.Axes,
    data_dict: dict,
    **kwargs,
) -> plt.Axes:
    if len(data_dict) > 1:
        data_dict = data_dict[0]
    sweep_param = get_step_parameter(data_dict)
    sweep_current = data_dict[sweep_param]
    persistent_current = data_dict["persistent_current"]

    base_label = f" {kwargs['label']}" if "label" in kwargs else ""
    kwargs.pop("label", None)
    ax.plot(sweep_current, persistent_current, "-o", label=f"{base_label}", **kwargs)
    ax.set_ylabel("Persistent Current (uA)")
    ax.set_xlabel(f"{sweep_param} (uA)")
    return ax


def plot_enable_read_sweep(ax: plt.Axes, dict_list, **kwargs):
    plot_read_sweep_array(
        ax, dict_list, "bit_error_rate", "enable_read_current", **kwargs
    )
    plot_fill_between_array(ax, dict_list)
    ax.axvline(IC0_C3, color="black", linestyle="--")
    ax.set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]")
    ax.set_ylabel("BER")
    ax.set_xlim(READ_XMIN, READ_XMAX)
    return ax



def plot_write_sweep(ax: Axes, dict_list: str, show_colorbar:bool=False) -> Axes:
    colors = CMAP(np.linspace(0.1, 1, len(dict_list)))
    write_temp_list = []
    enable_write_current_list = []
    for i, data_dict in enumerate(dict_list):
        x, y, ztotal = build_array(data_dict, "bit_error_rate")
        write_temp = get_channel_temperature(data_dict, "write")
        enable_write_current = get_enable_write_current(data_dict)
        write_temp_list.append(write_temp)
        enable_write_current_list.append(enable_write_current)
        ax.plot(
            y,
            ztotal,
            label=f"$T_{{W}}$ = {write_temp:.2f} K, $I_{{EW}}$ = {enable_write_current:.2f} $\mu$A",
            color=colors[i],
            marker=".",
        )
    set_ber_ticks(ax)
    if show_colorbar:
        add_colorbar(
            ax,
            write_temp_list,
            label="Enable Write Current [$\mu$A]",
            cmap=CMAP3,
        )
    return ax




def plot_read_sweep_array(
    ax: Axes,
    dict_list: list[dict],
    value_name: str,
    variable_name: str,
    show_colorbar=None,
    show_errorbar=False,
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
            show_errorbar=show_errorbar,
            **kwargs,
        )
        variable_list.append(data_dict[variable_name].flatten()[0] * 1e6)

    if show_colorbar:
        add_colorbar(
            ax,
            variable_list,
            label="Write Current [$\mu$A]",
            cmap=CMAP,
        )

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



def plot_read_switch_probability_array(
    ax: Axes, dict_list: list[dict], write_list=None, **kwargs
) -> Axes:
    colors = CMAP(np.linspace(0, 1, len(dict_list)))
    for i, data_dict in enumerate(dict_list):
        if write_list is not None:
            plot_read_sweep_switch_probability(
                ax,
                data_dict,
                color=colors[i],
                label=f"{write_list[i]} $\mu$A",
                **kwargs,
            )
        else:
            plot_read_sweep_switch_probability(ax, data_dict, color=colors[i])
    return ax


def plot_full_grid(axs, dict_list):
    plot_grid(axs[1:5, 0:4], dict_list)
    plot_row_or_column(axs[0, 0:4], dict_list, is_row=True)
    plot_row_or_column(axs[1:5, 4], dict_list, is_row=False)
    axs[0, 4].axis("off")
    axs[4, 0].set_xlabel("Enable Current ($\mu$A)")
    axs[4, 0].set_ylabel("Critical Current ($\mu$A)")
    return axs


def plot_row_or_column(axs, dict_list, is_row=True):
    colors = CMAP3(np.linspace(0.1, 1, 4))
    markers = ["o", "s", "D", "^"]
    for data_dict in dict_list:
        cell = get_current_cell(data_dict)
        column, row = convert_cell_to_coordinates(cell)
        x = data_dict["x"][0]
        y = data_dict["y"][0]
        ztotal = data_dict["ztotal"]
        xfit, yfit = get_fitting_points(x, y, ztotal)

        index = column if is_row else row
        axs[index].plot(
            xfit,
            yfit,
            label=f"{cell}",
            color=colors[column],
            marker=markers[row],
            markeredgecolor="k",
            markeredgewidth=0.1,
        )
        axs[index].legend(loc="upper right")
        axs[index].set_xlim(0, 600)
        axs[index].set_ylim(0, 1500)
    return axs


def plot_grid(axs: Axes, dict_list: list[dict]) -> Axes:
    colors = CMAP3(np.linspace(0.1, 1, 4))
    markers = ["o", "s", "D", "^"]
    for data_dict in dict_list:
        cell = get_current_cell(data_dict)

        column, row = convert_cell_to_coordinates(cell)
        x = data_dict["x"][0]
        y = data_dict["y"][0]
        ztotal = data_dict["ztotal"]
        xfit, yfit = get_fitting_points(x, y, ztotal)
        axs[row, column].plot(
            xfit,
            yfit,
            label=f"{cell}",
            color=colors[column],
            marker=markers[row],
        )
        y_step_size = y[1] - y[0]
        axs[row, column].errorbar(
            xfit,
            yfit,
            yerr=y_step_size* np.ones_like(yfit),
            fmt="o",
            color=colors[column],
            markeredgecolor="k",
            markeredgewidth=0.1,
            markersize=5,
            alpha=0.5,
            zorder=1,
            label="_data",
        )

        xfit, yfit = filter_plateau(xfit, yfit, yfit[0] * 0.75)

        plot_linear_fit(
            axs[row, column],
            xfit,
            yfit,
        )
        # plot_optimal_enable_currents(axs[row, column], data_dict)
        axs[row, column].legend(loc="upper right")
        axs[row, column].set_xlim(0, 600)
        axs[row, column].set_ylim(0, 1500)
    axs[-1, 0].set_xlabel("Enable Current ($\mu$A)")
    axs[-1, 0].set_ylabel("Critical Current ($\mu$A)")
    return axs



def plot_linear_fit(ax: Axes, xfit: np.ndarray, yfit: np.ndarray, add_text:bool=False) -> Axes:
    z = np.polyfit(xfit, yfit, 1)
    p = np.poly1d(z)
    x_intercept = -z[1] / z[0]
    # ax.scatter(xfit, yfit, color="#08519C")
    xplot = np.linspace(0, x_intercept, 10)
    ax.plot(xplot, p(xplot), ":", color="k")
    if add_text:
        ax.text(
            0.1,
            0.1,
            f"{p[1]:.3f}x + {p[0]:.3f}\n$x_{{int}}$ = {x_intercept:.2f}",
            fontsize=12,
            color="red",
            backgroundcolor="white",
            transform=ax.transAxes,
        )
    ax.set_xlim((0, 600))
    ax.set_ylim((0, 2000))

    return ax
