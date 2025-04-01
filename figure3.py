import os

import ltspice
import numpy as np
from matplotlib import pyplot as plt

from analysis.plotting import (
    create_plot,
    plot_current_sweep_ber,
    plot_current_sweep_switching,
    plot_read_sweep_array,
    plot_read_switch_probability_array,
)
from analysis.utils import (
    CMAP,
    filter_first,
    import_directory,
    process_read_data,
)

if __name__ == "__main__":

    # get raw files
    files = os.listdir("data/figure3/")
    files = [f for f in files if f.endswith(".raw")]
    # Sort files by write current
    write_current_list = []
    for file in files:
        data = ltspice.Ltspice(
            f"data/figure3/{file}"
        ).parse()
        ltsp_data_dict = process_read_data(data)
        write_current = ltsp_data_dict[0]["write_current"][0]
        write_current_list.append(write_current * 1e6)

    sorted_args = np.argsort(write_current_list)
    files = [files[i] for i in sorted_args]

    ltsp_data = ltspice.Ltspice(
        "data/figure3/nmem_cell_read_example_trace.raw"
    ).parse()
    ltsp_data_dict = process_read_data(ltsp_data)

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

    dict_list = import_directory(
        "/home/omedeiro/nmem/src/nmem/analysis/read_current_sweep_write_current2/write_current_sweep_C3"
    )
    dict_list = dict_list[::2]
    write_current_list = []
    for data_dict in dict_list:
        write_current = filter_first(data_dict["write_current"])
        write_current_list.append(write_current * 1e6)

    sorted_args = np.argsort(write_current_list)
    dict_list = [dict_list[i] for i in sorted_args]
    write_current_list = [write_current_list[i] for i in sorted_args]

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
    # ax.axvline(IRM, color="black", linestyle="--", linewidth=0.5)
    axs["B"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)
    axs["D"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)

    axs["C"].set_xlim(650, 850)
    axs["D"].set_xlim(650, 850)
    axs["C"].set_xlabel("$I_{\mathrm{read}}$ [$\mu$A]", labelpad=-1)
    axs["C"].set_ylabel("BER")
    axs["B"].set_ylabel("Switching Probability")
    axs["D"].set_ylabel("Switching Probability")

    # fig, ax = plt.subplots(4, 1, figsize=(6, 3))

    # plot_current_sweep_output(ax[0], data_dict)
    colors = CMAP(np.linspace(0, 1, len(dict_list)))
    col_set = [colors[i] for i in [0, 2, -1]]
    files = [files[i] for i in [0, 2, 11]]
    max_write_current = 300
    for i, file in enumerate(files):
        data = ltspice.Ltspice(
            f"/home/omedeiro/nmem/src/nmem/analysis/read_current_sweep_sim/{file}"
        ).parse()
        ltsp_data_dict = process_read_data(data)
        ltsp_write_current = ltsp_data_dict[0]["write_current"][0]
        plot_current_sweep_ber(
            axs["C"],
            ltsp_data_dict,
            color=CMAP(ltsp_write_current / max_write_current),
            label=f"{ltsp_write_current} $\mu$A",
            marker=".",
            linestyle="-",
            markersize=5,
        )

        plot_current_sweep_switching(
            axs["D"],
            ltsp_data_dict,
            color=CMAP(ltsp_write_current / max_write_current),
            label=f"{ltsp_write_current} $\mu$A",
            marker=".",
            markersize=5,
        )

    axs["A"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)
    axs["B"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)
    axs["C"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)
    axs["D"].axvline(case_current, color="black", linestyle="--", linewidth=0.5)

    # axs["A"].legend(loc="upper left", bbox_to_anchor=(1.0, 1.05))
    axs["B"].legend(
        loc="upper right",
        labelspacing=0.1,
        fontsize=6,
    )
    # axs["C"].legend(
    #     loc="upper right",
    # )
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
