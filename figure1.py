import matplotlib.pyplot as plt

from analysis.constants import import_directory
from plotting.style import apply_snm_style, set_figsize_square
from plotting.transients import plot_voltage_hist, plot_voltage_trace_averaged

apply_snm_style()


def plot_histogram():
    """
    Plot a histogram of voltage data from the specified directory.
    """
    fig, ax = plt.subplots(figsize=set_figsize_square())
    data = import_directory("data/figure1")
    plot_voltage_hist(ax, data[1])
    plt.show()


def plot_waveforms():
    """
    Plot averaged voltage waveforms with twin axes for enable traces.
    """
    data = import_directory("data/figure1")
    fig, ax_dict = plt.subplot_mosaic(
        [["A"], ["B"]],
        figsize=set_figsize_square(),
        constrained_layout=True,
    )

    ax_enable_write = ax_dict["A"].twinx()
    ax_enable_read = ax_dict["B"].twinx()

    # Plot waveforms
    plot_voltage_trace_averaged(
        ax_dict["A"], data[4], "trace_write_avg", color="#293689", label="Write"
    )
    plot_voltage_trace_averaged(
        ax_enable_write, data[4], "trace_ewrite_avg", color="#ff1423", label="Enable Write"
    )
    plot_voltage_trace_averaged(
        ax_dict["B"], data[4], "trace_read0_avg", color="#1966ff", label="Read 0"
    )
    plot_voltage_trace_averaged(
        ax_dict["B"], data[4], "trace_read1_avg", color="#ff7f0e", linestyle="--", label="Read 1"
    )
    plot_voltage_trace_averaged(
        ax_enable_read, data[4], "trace_eread_avg", color="#ff1423", label="Enable Read"
    )

    # Set labels
    ax_dict["A"].set_ylabel("[mV]")
    ax_enable_write.set_ylabel("[mV]")
    ax_dict["B"].set_ylabel("[mV]")
    ax_enable_read.set_ylabel("[mV]")
    ax_dict["B"].set_xlabel("Time [$\mu$s]")

    # Add legends
    ax_dict["A"].legend(loc="upper left")
    ax_enable_write.legend(loc="upper right")
    ax_dict["B"].legend(loc="upper left")
    ax_enable_read.legend(loc="upper right")

    plt.show()


if __name__ == "__main__":
    plot_histogram()
    plot_waveforms()
