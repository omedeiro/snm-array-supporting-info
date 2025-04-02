import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from analysis.constants import (
    get_channel_temperature,
    import_directory,
)
from plotting.style import add_dict_colorbar, apply_snm_style, set_figsize_wide
from plotting.sweeps import (
    plot_fill_between_array,
    plot_read_sweep_array,
)

apply_snm_style()


def main():
    enable_read_290_list = import_directory("data/figure2/data_290uA")
    enable_read_300_list = import_directory("data/figure2/data_300uA")
    enable_read_310_list = import_directory("data/figure2/data_310uA")


    dict_list = [enable_read_290_list, enable_read_300_list, enable_read_310_list]
    fig = plt.figure(figsize=set_figsize_wide())
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.05], wspace=0.5)

    axs = [fig.add_subplot(gs[i]) for i in range(3)]
    cax = fig.add_subplot(gs[3])  # Dedicated colorbar axis

    for i, ax in enumerate(axs):
        plot_read_sweep_array(ax, dict_list[i], "bit_error_rate", "enable_read_current")
        enable_write_temp = get_channel_temperature(dict_list[i][0], "write")
        plot_fill_between_array(ax, dict_list[i])
        ax.set_xlim(400, 1000)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Read Current ($\mu$A)")
        ax.set_title(
            f"$I_{{EW}}$ = {290 + i * 10} $\mu$A\n $T_{{write}}$ = {enable_write_temp:.2f} K"
        )
        ax.set_box_aspect(1.0)

    axs[0].set_ylabel("Bit Error Rate")

    axpos = axs[2].get_position()
    cbar = add_dict_colorbar(axs[2], dict_list, "enable_read_current", cax=cax)
    cbar.ax.set_position([axpos.x1 + 0.02, axpos.y0, 0.01, axpos.y1 - axpos.y0])
    cbar.set_ticks([150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250])

    plt.show()


if __name__ == "__main__":
    main()
