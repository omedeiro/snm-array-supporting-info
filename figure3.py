import os

import ltspice
import numpy as np
from matplotlib import pyplot as plt

from analysis.constants import (
    filter_first,
    import_directory,
    process_read_data,
)
from plotting.style import CMAP, apply_snm_style
from plotting.sweeps import (
    plot_current_sweep_ber,
    plot_current_sweep_switching,
    plot_read_sweep_array,
    plot_read_switch_probability_array,
)
from plotting.transients import (
    create_plot,
)

apply_snm_style()


if __name__ == "__main__":

    # Get and parse raw files
    files = [
        f for f in os.listdir("data/figure3/read_current_sweep/") if f.endswith(".raw")
    ]
    parsed_data = {}
    write_current_list = []

    for file in files:
        data = ltspice.Ltspice(f"data/figure3/read_current_sweep/{file}").parse()
        ltsp_data_dict = process_read_data(data)
        parsed_data[file] = ltsp_data_dict
        write_current = ltsp_data_dict[0]["write_current"][0] * 1e6
        write_current_list.append(write_current)

    # Sort files and data by write current
    sorted_files_data = sorted(zip(files, write_current_list), key=lambda x: x[1])
    files, write_current_list = zip(*sorted_files_data)

    # Parse example trace once
    ltsp_data_dict = parsed_data["nmem_cell_read_example_trace.raw"]

    inner = [
        ["T0", "T1", "T2", "T3"],
    ]
    innerb = [
        ["B0", "B1", "B2", "B3"],
    ]
    inner2 = [
        ["A", "B"],
    ]
    inner3 = [
        ["C", "D"],
    ]
    outer_nested_mosaic = [
        [inner],
        [innerb],
        [inner2],
        [inner3],
    ]
    fig, axs = plt.subplot_mosaic(
        outer_nested_mosaic,
        figsize=(180 / 25.4, 180 / 25.4),
        height_ratios=[2, 0.5, 1, 1],
    )

    CASE = 16
    create_plot(axs, ltsp_data_dict, cases=[CASE])
    case_current = ltsp_data_dict[CASE]["read_current"][CASE]

    handles, labels = axs["T0"].get_legend_handles_labels()
    # Select specific items
    selected_labels = [
        "Left Branch Current",
        "Right Branch Current",
        "Left Critical Current",
        "Right Critical Current",
    ]
    selected_labels2 = [
        "$i_{\mathrm{H_L}}$",
        "$i_{\mathrm{H_R}}$",
        "$I_{\mathrm{c,H_L}}$",
        "$I_{\mathrm{c,H_R}}$",
    ]
    selected_handles = [handles[labels.index(lbl)] for lbl in selected_labels]

    dict_list = import_directory("data/figure3/write_current_sweep")[::2]
    write_current_list = [
        filter_first(data_dict["write_current"]) * 1e6 for data_dict in dict_list
    ]

    # Sort dict_list and write_current_list together
    sorted_dicts = sorted(zip(dict_list, write_current_list), key=lambda x: x[1])
    dict_list, write_current_list = zip(*sorted_dicts)

    plot_read_sweep_array(
        axs["A"],
        dict_list,
        "bit_error_rate",
        "write_current",
        marker=".",
        linestyle="-",
        markersize=4,
    )
    axs["A"].set_xlim(650, 850)
    axs["A"].set_ylabel("BER")
    axs["A"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)
    plot_read_switch_probability_array(
        axs["B"], dict_list, write_current_list, marker=".", linestyle="-", markersize=2
    )
    axs["B"].set_xlim(650, 850)
    axs["B"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)
    axs["D"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)

    axs["C"].set_xlim(650, 850)
    axs["D"].set_xlim(650, 850)
    axs["C"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)
    axs["C"].set_ylabel("BER")
    axs["B"].set_ylabel("Switching Probability")
    axs["D"].set_ylabel("Switching Probability")

    colors = CMAP(np.linspace(0, 1, len(dict_list)))
    col_set = [colors[i] for i in [0, 2, -1]]
    selected_files = [files[i] for i in [0, 2, 11]]
    max_write_current = 300

    for file in selected_files:
        ltsp_data_dict = parsed_data[file]
        ltsp_write_current = ltsp_data_dict[0]["write_current"][0]
        normalized_color = CMAP(ltsp_write_current / max_write_current)

        plot_current_sweep_ber(
            axs["C"],
            ltsp_data_dict,
            color=normalized_color,
            label=f"{ltsp_write_current} $\mu$A",
            marker=".",
            linestyle="-",
            markersize=5,
        )
        plot_current_sweep_switching(
            axs["D"],
            ltsp_data_dict,
            color=normalized_color,
            label=f"{ltsp_write_current} $\mu$A",
            marker=".",
            markersize=5,
        )

    axs["A"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)
    axs["B"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)
    axs["C"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)
    axs["D"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)

    axs["B"].legend(
        loc="upper right",
        labelspacing=0.1,
        fontsize=6,
    )
    axs["D"].legend(
        loc="upper right",
        labelspacing=0.1,
        fontsize=6,
    )

    fig.subplots_adjust(hspace=0.5, wspace=0.5)
    fig.patch.set_alpha(0)

    ax_legend = fig.add_axes([0.5, 0.9, 0.1, 0.01])
    ax_legend.axis("off")
    ax_legend.legend(
        selected_handles,
        selected_labels2,
        loc="center",
        ncol=4,
        bbox_to_anchor=(0.0, 1.0),
        frameon=False,
        handlelength=2.5,
        fontsize=8,
    )

    plt.show()
