import os
from typing import Literal

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib import colors as mcolors
from matplotlib.axes import Axes
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator

from analysis.utils import (
    build_array,
    get_bit_error_rate,
    get_channel_temperature,
    get_enable_current_sweep,
    get_enable_read_current,
    get_enable_write_current,
    get_read_currents,
    get_read_width,
    get_step_parameter,
    get_voltage_trace_data,
    get_write_current,
    get_write_width,
    polygon_inverting,
    polygon_nominal,
)

READ_XMIN = 400
READ_XMAX = 1000
IC0_C3 = 910
CMAP = plt.get_cmap("coolwarm")
if os.name == "Windows":
    font_path = r"C:\\Users\\ICE\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Inter-VariableFont_opsz,wght.ttf"
if os.name == "posix":
    font_path = "/home/omedeiro/Inter-VariableFont_opsz,wght.ttf"
fm.fontManager.addfont(font_path)
prop = fm.FontProperties(fname=font_path)

FILL_WIDTH = 5
VOUT_YMAX = 40
VOLTAGE_THRESHOLD = 2.0e-3

plt.rcParams.update(
    {
        "figure.figsize": [3.5, 3.5],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 7,
        "axes.linewidth": 0.5,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "font.family": "Inter",
        "lines.markersize": 2,
        "lines.linewidth": 1.5,
        "legend.fontsize": 5,
        "legend.frameon": False,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 2,
        "ytick.minor.size": 2,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
    }
)


COLORS = [
    "#1b9e77",  # Teal green
    "#d95f02",  # Burnt orange
    "#7570b3",  # Muted blue-purple
    "#e7298a",  # Reddish pink
    "#66a61e",  # Olive green
    "#e6ab02",  # Mustard yellow
    "#a6761d",  # Brown
    "#666666",  # Dark gray
]

plt.rcParams["axes.prop_cycle"] = cycler(color=COLORS)




def plot_write_sweep(ax: Axes, dict_list: str) -> Axes:
    # colors = CMAP(np.linspace(0.1, 1, len(dict_list)))
    colors = CMAP(np.linspace(0.1, 1, len(dict_list)))
    write_temp_list = []
    enable_write_current_list = []
    for i, data_dict in enumerate(dict_list):
        x, y, ztotal = build_array(data_dict, "bit_error_rate")
        _, _, zswitch = build_array(data_dict, "total_switches_norm")
        write_temp = get_channel_temperature(data_dict, "write")
        enable_write_current = get_enable_write_current(data_dict)
        write_temp_list.append(write_temp)
        enable_write_current_list.append(enable_write_current)
        ax.plot(
            y,
            ztotal,
            label=f"$T_{{W}}$ = {write_temp:.2f} K, $I_{{EW}}$ = {enable_write_current:.2f} $\mu$A",
            color=colors[dict_list.index(data_dict)],
            marker=".",
        )
    ax.set_ylim([0, 1])
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    norm = mcolors.Normalize(
        vmin=min(enable_write_current_list), vmax=max(enable_write_current_list)
    )
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
    cbar.set_label("Enable Write Current [$\mu$A]")
    return ax



def plot_enable_write_sweep_multiple(
    ax: Axes,
    dict_list: list[dict],
    add_errorbar: bool = False,
    N: int = None,
    add_colorbar: bool = True,
) -> Axes:
    if N is None:
        N = len(dict_list)
    colors = CMAP(np.linspace(0, 1, N))
    write_current_list = []
    for data_dict in dict_list:
        write_current = get_write_current(data_dict)
        write_current_list.append(write_current)

    for i, data_dict in enumerate(dict_list):
        write_current_norm = write_current_list[i] / 100
        plot_enable_sweep_single(
            ax, data_dict, color=CMAP(write_current_norm), add_errorbar=add_errorbar
        )

    if add_colorbar:
        norm = mcolors.Normalize(
            vmin=min(write_current_list), vmax=max(write_current_list)
        )  # Normalize for colormap
        sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)
        cbar.set_label("Write Current [$\mu$A]")

    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    return ax


def plot_enable_sweep_single(
    ax: Axes,
    data_dict: dict,
    add_errorbar: bool = False,
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
    if add_errorbar:
        # ax.errorbar(
        #     enable_currents,
        #     bit_error_rate,
        #     yerr=np.sqrt(bit_error_rate * (1 - bit_error_rate) / len(bit_error_rate)),
        #     **kwargs,
        # )
        ax.fill_between(
            enable_currents,
            bit_error_rate
            - np.sqrt(bit_error_rate * (1 - bit_error_rate) / len(bit_error_rate)),
            bit_error_rate
            + np.sqrt(bit_error_rate * (1 - bit_error_rate) / len(bit_error_rate)),
            alpha=0.1,
            color=kwargs.get("color"),
        )
    ax.set_xlim(enable_currents[0], enable_currents[-1])
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_major_locator(MultipleLocator(25))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    return ax


def plot_parameter_array(
    ax: Axes,
    xloc: np.ndarray,
    yloc: np.ndarray,
    parameter_array: np.ndarray,
    title: str = None,
    log: bool = False,
    reverse: bool = False,
    cmap: plt.cm = None,
) -> Axes:
    if cmap is None:
        cmap = plt.get_cmap("viridis")
    if reverse:
        cmap = cmap.reversed()

    if log:
        ax.matshow(
            parameter_array,
            cmap=cmap,
            norm=LogNorm(vmin=np.min(parameter_array), vmax=np.max(parameter_array)),
        )
    else:
        ax.matshow(parameter_array, cmap=cmap)

    if title:
        ax.set_title(title)
    ax.set_xticks(range(4), ["A", "B", "C", "D"])
    ax.set_yticks(range(4), ["1", "2", "3", "4"])
    ax.tick_params(axis="both", length=0)
    return ax




def plot_fill_between(ax, data_dict, fill_color):
    # fill the area between 0.5 and the curve
    enable_write_currents = get_enable_current_sweep(data_dict)
    bit_error_rate = get_bit_error_rate(data_dict)
    verts = polygon_nominal(enable_write_currents, bit_error_rate)
    poly = PolyCollection([verts], facecolors=fill_color, alpha=0.3, edgecolors="k")
    ax.add_collection(poly)
    verts = polygon_inverting(enable_write_currents, bit_error_rate)
    poly = PolyCollection([verts], facecolors=fill_color, alpha=0.3, edgecolors="k")
    ax.add_collection(poly)

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
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.set_ylim(0, 1)
    return ax



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
    add_errorbar: bool = False,
    **kwargs,
) -> Axes:
    write_temp = None
    label = None
    read_currents = get_read_currents(data_dict)

    if value_name == "bit_error_rate":
        value = get_bit_error_rate(data_dict)
    if value_name == "write_0_read_1":
        value = data_dict.get("write_0_read_1").flatten()
    if value_name == "write_1_read_0":
        value = data_dict.get("write_1_read_0").flatten()

    if variable_name == "write_current":
        variable = get_write_current(data_dict)
        label = f"{variable:.2f}$\mu$A"
    if variable_name == "enable_write_current":
        variable = get_enable_write_current(data_dict)
        write_temp = get_channel_temperature(data_dict, "write")
        if write_temp is None:
            label = f"{variable:.2f}$\mu$A"
        else:
            label = f"{variable:.2f}$\mu$A, {write_temp:.2f}K"
    if variable_name == "read_width":
        variable = get_read_width(data_dict)
        label = f"{variable:.2f} pts "
    if variable_name == "write_width":
        variable = get_write_width(data_dict)
        label = f"{variable:.2f} pts "
    if variable_name == "enable_read_current":
        variable = get_enable_read_current(data_dict)
        read_temp = get_channel_temperature(data_dict, "read")
        label = f"{variable:.2f}$\mu$A, {read_temp:.2f}K"

    ax.plot(
        read_currents,
        value,
        label=label,
        **kwargs,
    )
    if add_errorbar:
        # ax.errorbar(
        #     read_currents,
        #     value,
        #     yerr=np.sqrt(value * (1 - value) / len(value)),
        #     **kwargs,
        # )
        ax.fill_between(
            read_currents,
            value - np.sqrt(value * (1 - value) / len(value)),
            value + np.sqrt(value * (1 - value) / len(value)),
            alpha=0.1,
            color=kwargs.get("color"),
        )
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
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


def plot_voltage_trace_averaged(
    ax: Axes, data_dict: dict, trace_name: str, **kwargs
) -> Axes:
    x, y = get_voltage_trace_data(data_dict, trace_name)
    ax.plot(
        (x - x[0]),
        y,
        **kwargs,
    )
    return ax


def plot_voltage_hist(ax: Axes, data_dict: dict) -> Axes:
    ax.hist(
        data_dict["read_zero_top"][0, :],
        log=True,
        range=(0.2, 0.6),
        bins=100,
        label="Read 0",
        color="#1966ff",
        alpha=0.5,
    )
    ax.hist(
        data_dict["read_one_top"][0, :],
        log=True,
        range=(0.2, 0.6),
        bins=100,
        label="Read 1",
        color="#ff1423",
        alpha=0.5,
    )
    ax.set_xlabel("Voltage [V]")
    ax.set_ylabel("Counts")
    ax.legend()
    return ax

def plot_read_switch_probability_array(
    ax: Axes, dict_list: list[dict], write_list=None, **kwargs
) -> Axes:
    colors = CMAP(np.linspace(0, 1, len(dict_list)))
    print(f"len dict_list: {len(dict_list)}")
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


def plot_transient(
    ax: plt.Axes,
    data_dict: dict,
    cases=[0],
    signal_name: str = "tran_left_critical_current",
    **kwargs,
) -> plt.Axes:
    for i in cases:
        data = data_dict[i]
        time = data["time"]
        signal = data[signal_name]
        ax.plot(time, signal, **kwargs)
    # ax.set_xlabel("Time (s)")
    # ax.set_ylabel(f"{signal_name}")
    # ax.legend(loc="upper right")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    return ax



def plot_transient_fill(
    ax: plt.Axes,
    data_dict: dict,
    cases=[0],
    s1: str = "tran_left_critical_current",
    s2: str = "tran_left_branch_current",
    **kwargs,
) -> plt.Axes:
    for i in cases:
        data = data_dict[i]
        time = data["time"]
        signal1 = data[s1]
        signal2 = data[s2]
        ax.fill_between(
            time,
            signal2,
            signal1,
            color=CMAP(0.5),
            alpha=0.5,
            label="Left Branch",
            **kwargs,
        )
    return ax


def plot_transient_fill_branch(
    ax: plt.Axes, data_dict: dict, cases=[0], side: Literal["left", "right"] = "left"
) -> plt.Axes:
    for i in cases:
        data_dict = data_dict[i]
        time = data_dict["time"]
        if side == "left":
            left_critical_current = data_dict["tran_left_critical_current"]
            left_branch_current = data_dict["tran_left_branch_current"]
            ax.fill_between(
                time,
                left_branch_current,
                left_critical_current,
                color=CMAP(0.5),
                alpha=0.5,
                label="Left Branch",
            )
        if side == "right":
            right_critical_current = data_dict["tran_right_critical_current"]
            right_branch_current = data_dict["tran_right_branch_current"]
            ax.fill_between(
                time,
                right_branch_current,
                right_critical_current,
                color=CMAP(0.5),
                alpha=0.5,
                label="Right Branch",
            )
    return ax


def plot_fill_between_array(ax: Axes, dict_list: list[dict]) -> Axes:
    colors = CMAP(np.linspace(0.1, 1, len(dict_list)))
    for i, data_dict in enumerate(dict_list):
        plot_fill_between(ax, data_dict, colors[i])
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
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.set_xlim(650, 850)
    ax.xaxis.set_major_locator(plt.MultipleLocator(50))
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
    # ax.set_ylabel("switching_probability")
    # ax.set_xlabel(f"{sweep_param} (uA)")
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.5))
    ax.set_xlim(650, 850)
    ax.xaxis.set_major_locator(plt.MultipleLocator(50))
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



def plot_case(ax, data_dict, case, signal_name="left", color=None):
    if color is None:
        if signal_name == "left":
            color = "C0"
        elif signal_name == "right":
            color = "C1"

    plot_transient(
        ax,
        data_dict,
        cases=[case],
        signal_name=f"tran_{signal_name}_critical_current",
        linestyle="--",
        color=color,
        label=f"{signal_name.capitalize()} Critical Current",
    )
    plot_transient(
        ax,
        data_dict,
        cases=[case],
        signal_name="tran_left_branch_current",
        color="C0",
        label="Left Branch Current",
    )
    plot_transient(
        ax,
        data_dict,
        cases=[case],
        signal_name="tran_right_branch_current",
        color="C1",
        label="Right Branch Current",
    )


def plot_case_vout(ax, data_dict, case, signal_name, **kwargs):
    ax = plot_transient(
        ax, data_dict, cases=[case], signal_name=f"{signal_name}", **kwargs
    )
    ax.yaxis.set_major_locator(plt.MultipleLocator(50e-3))
    pos = ax.get_position()
    ax.set_position([pos.x0, pos.y0+0.1, pos.width, pos.height / 1.6])


def create_plot(
    axs: list[plt.Axes], data_dict: dict, cases: list[int]
) -> list[plt.Axes]:

    write_current = data_dict[0]["write_current"][0]

    time_windows = {
        0: (100e-9, 150e-9),
        1: (200e-9, 250e-9),
        2: (300e-9, 350e-9),
        3: (400e-9, 450e-9),
    }
    sweep_param_list = []
    for case in cases:
        for i, time_window in time_windows.items():
            sweep_param = data_dict[case]["read_current"]
            sweep_param = sweep_param[case]
            sweep_param_list.append(sweep_param)
            ax: plt.Axes = axs[f"T{i}"]
            plot_case(ax, data_dict, case, "left")
            plot_case(ax, data_dict, case, "right")
            ax.plot(
                data_dict[case]["time"],
                -1 * data_dict[case]["tran_left_critical_current"],
                color="C0",
                linestyle="--",
            )
            ax.plot(
                data_dict[case]["time"],
                -1 * data_dict[case]["tran_right_critical_current"],
                color="C1",
                linestyle="--",
            )
            ax.set_ylim(-300, 900)
            ax.set_xlim(time_window)
            ax.yaxis.set_major_locator(plt.MultipleLocator(500))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(100))

            ax.set_ylabel("I ($\mu$A)", labelpad=-4)
            ax.set_xlabel("Time (ns)", labelpad=-3)
            ax.yaxis.set_major_locator(plt.MultipleLocator(250))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(50))
            ax.xaxis.set_major_locator(plt.MultipleLocator(50e-9))
            ax.xaxis.set_minor_locator(plt.MultipleLocator(10e-9))
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*1e9:.0f}"))



            ax: plt.Axes = axs[f"B{i}"]
            plot_case_vout(ax, data_dict, case, "tran_output_voltage", color="k")
            ax.set_ylim(-50e-3, 50e-3)
            ax.set_xlim(time_window)
            ax.axhline(0, color="black", linestyle="--", linewidth=0.5)
            ax.yaxis.set_major_locator(plt.MultipleLocator(50e-3))
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*1e3:.0f}"))
            ax.set_xlabel("Time (ns)", labelpad=-3)
            ax.set_ylabel("V (mV)", labelpad=-3)
            ax.xaxis.set_major_locator(plt.MultipleLocator(50e-9))
            ax.xaxis.set_minor_locator(plt.MultipleLocator(10e-9))
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*1e9:.0f}"))
    return axs

