import matplotlib.pyplot as plt

from analysis.utils import (
    import_directory,
)
from plotting.style import (
    apply_snm_style,
    set_figsize_square,
)  # Import the function for standard small figure size
from plotting.transients import (
    plot_voltage_hist,
    plot_voltage_trace_averaged,
)

apply_snm_style()  # Apply the style settings


def plot_figure1_histogram():
    fig, ax = plt.subplots(figsize=set_figsize_square())  # Use set_figsize_small
    dict_list = import_directory("data/figure1")
    plot_voltage_hist(ax, dict_list[1])
    plt.show()


def plot_figure1_waveforms():
    dict_list = import_directory("data/figure1")
    fig, ax_dict = plt.subplot_mosaic(
        [["A"], ["B"]],
        figsize=set_figsize_square(),  # Use set_figsize_small
        constrained_layout=True,
    )

    # Twin axes for enable traces
    ax2 = ax_dict["A"].twinx()
    ax3 = ax_dict["B"].twinx()

    # Plot waveforms
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

    # Labels and legends
    ax_dict["A"].set_ylabel("[mV]")
    ax2.set_ylabel("[mV]")
    ax_dict["B"].set_ylabel("[mV]")
    ax3.set_ylabel("[mV]")
    ax_dict["B"].set_xlabel("Time [$\mu$s]")

    # Handle legends
    ax_dict["A"].legend(loc="upper left")
    ax2.legend(loc="upper right")
    ax_dict["B"].legend(loc="upper left")
    ax3.legend(loc="upper right")

    plt.show()


if __name__ == "__main__":
    plot_figure1_histogram()
    plot_figure1_waveforms()
