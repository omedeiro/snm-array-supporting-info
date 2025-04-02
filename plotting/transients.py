from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from analysis.data_processing import (
    get_voltage_trace_data,
)
from plotting.style import CMAP


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

