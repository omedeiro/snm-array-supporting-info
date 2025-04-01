import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from nmem.analysis.analysis import (
    import_directory,
    plot_fill_between_array,
    plot_read_sweep_array,
    get_channel_temperature,
    CMAP3,
)
from nmem.analysis.read_current_sweep_write_current2.write_current_sweep import (
    add_colorbar,
)

# font_path = r"C:\\Users\\ICE\\AppData\\Local\\Microsoft\\Windows\\Fonts\\Inter-VariableFont_opsz,wght.ttf"
# fm.fontManager.addfont(font_path)
# prop = fm.FontProperties(fname=font_path)

# plt.rcParams.update(
#     {
#         "figure.figsize": [3.5, 3.5],
#         "font.size": 6,
#         "axes.linewidth": 0.5,
#         "xtick.major.width": 0.5,
#         "ytick.major.width": 0.5,
#         "xtick.direction": "out",
#         "ytick.direction": "out",
#         "font.family": "Inter",
#         "lines.markersize": 2,
#         "lines.linewidth": 1.2,
#         "legend.fontsize": 5,
#         "legend.frameon": False,
#         "xtick.major.size": 1,
#         "ytick.major.size": 1,
#     }
# )

if __name__ == "__main__":
    data = import_directory("data")

    enable_read_290_list = import_directory("data_290uA")
    enable_read_300_list = import_directory("data_300uA")
    enable_read_310_list = import_directory("data_310uA")
    enable_read_310_C4_list = import_directory("data_310uA_C4")

    data_inverse = import_directory("data_inverse")

    dict_list = [enable_read_290_list, enable_read_300_list, enable_read_310_list]
    fig = plt.figure(figsize=(180 / 25.4, 90 / 25.4))
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.5)

    axs = [fig.add_subplot(gs[i]) for i in range(3)]
    cax = fig.add_subplot(gs[3])  # dedicated colorbar axis
    for i in range(3):
        plot_read_sweep_array(
            axs[i], dict_list[i], "bit_error_rate", "enable_read_current"
        )
        enable_write_temp = get_channel_temperature(dict_list[i][0], "write")
        plot_fill_between_array(axs[i], dict_list[i])
        axs[i].set_xlim(400, 1000)
        axs[i].set_ylim(0, 1)
        axs[i].set_xlabel("Read Current ($\mu$A)")
        axs[i].set_title(
            f"Enable Write Current = {290 + i * 10} $\mu$A\n $T_{{write}}$ = {enable_write_temp:.2f} K"
        )
        axs[i].set_box_aspect(1.0)
    axs[0].set_ylabel("Bit Error Rate")
    # axs[2].legend(
    #     frameon=False,
    #     loc="upper left",
    #     bbox_to_anchor=(1, 1),
    #     title="Enable Read Current,\n Read Temperature",
    # )

    axpos = axs[2].get_position()
    cbar = add_colorbar(axs[2], dict_list, "enable_read_current", cax=cax)
    cbar.ax.set_position([axpos.x1 + 0.02, axpos.y0, 0.01, axpos.y1 - axpos.y0])
    cbar.set_ticks([150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250])

    plt.savefig("read_current_sweep_three.pdf", bbox_inches="tight")
