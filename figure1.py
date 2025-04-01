import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import os
from analysis.utils import (
    import_directory,
    get_bit_error_rate,
)
from analysis.plotting import (
    plot_voltage_trace_averaged,
    plot_voltage_hist,
)

def plot_read_delay(ax: Axes, dict_list: list[dict]) -> Axes:
    bers = []
    for i in range(4):
        bers.append(get_bit_error_rate(dict_list[i]))

    ax.plot([1, 2, 3, 4], bers, label="bit_error_rate", marker="o", color="#345F90")
    ax.set_xlabel("Delay [$\mu$s]")
    ax.set_ylabel("BER")

    return ax


def create_trace_hist_plot(
    ax_dict: dict[str, Axes], dict_list: list[dict], save: bool = False
) -> Axes:
    ax2 = ax_dict["A"].twinx()
    ax3 = ax_dict["B"].twinx()

    plot_voltage_trace_averaged(
        ax_dict["A"], dict_list[4], "trace_write_avg", color="#293689", label="Write"
    )
    plot_voltage_trace_averaged(
        ax2, dict_list[4], "trace_ewrite_avg", color="#ff1423", label="Enable Write"
    )
    plot_voltage_trace_averaged(
        ax_dict["B"], dict_list[4], "trace_read0_avg", color="#1966ff", label="Read 0"
    )
    plot_voltage_trace_averaged(
        ax_dict["B"],
        dict_list[4],
        "trace_read1_avg",
        color="#ff7f0e",
        linestyle="--",
        label="Read 1",
    )
    plot_voltage_trace_averaged(
        ax3, dict_list[4], "trace_eread_avg", color="#ff1423", label="Enable Read"
    )

    plot_voltage_hist(ax_dict["C"], dict_list[3])

    ax_dict["A"].legend(loc="upper left")
    ax_dict["A"].set_ylabel("[mV]")
    ax2.legend()
    ax2.set_ylabel("[mV]")
    ax3.legend()
    ax3.set_ylabel("[mV]")
    ax_dict["B"].set_xlabel("Time [$\mu$s]")
    ax_dict["B"].set_ylabel("[mV]")
    ax_dict["B"].legend(loc="upper left")

    return ax_dict

def plot_figure1_histogram():
    fig, ax = plt.subplots(figsize=(60 / 25.4, 45 / 25.4))
    dict_list = import_directory("data/figure1")
    plot_voltage_hist(ax, dict_list[1])
    plt.show()

def plot_figure1_waveforms():
    dict_list = import_directory("data/figure1")
    fig, ax_dict = plt.subplot_mosaic(
        "A;B", figsize=(60 / 25.4, 45 / 25.4), constrained_layout=True
    )
    ax2 = ax_dict["A"].twinx()
    ax3 = ax_dict["B"].twinx()
    plot_voltage_trace_averaged(
        ax_dict["A"], dict_list[4], "trace_write_avg", color="#293689", label="Write"
    )
    plot_voltage_trace_averaged(
        ax2, dict_list[4], "trace_ewrite_avg", color="#ff1423", label="Enable Write"
    )
    plot_voltage_trace_averaged(
        ax_dict["B"], dict_list[4], "trace_read0_avg", color="#1966ff", label="Read 0"
    )
    plot_voltage_trace_averaged(
        ax_dict["B"],
        dict_list[4],
        "trace_read1_avg",
        color="#ff7f0e",
        linestyle="--",
        label="Read 1",
    )
    plot_voltage_trace_averaged(
        ax3, dict_list[4], "trace_eread_avg", color="#ff1423", label="Enable Read"
    )

    ax_dict["A"].legend(loc="upper left")
    ax_dict["A"].set_ylabel("[mV]")
    ax2.legend()
    ax2.set_ylabel("[mV]")
    ax3.legend()
    ax3.set_ylabel("[mV]")
    ax_dict["B"].set_xlabel("Time [$\mu$s]")
    ax_dict["B"].set_ylabel("[mV]")
    ax_dict["B"].legend(loc="upper left")

    plt.show()
if __name__ == "__main__":
    plot_figure1_histogram()

    plot_figure1_waveforms()

    