import os

import matplotlib.pyplot as plt

from analysis.utils import import_directory
from plotting.style import apply_snm_style
from plotting.sweeps import plot_enable_write_sweep_multiple

apply_snm_style()



def main():
    fig, axs = plt.subplot_mosaic("BC", figsize=(180 / 25.4, 90 / 25.4))

    dict_list = import_directory(
        os.path.join(os.path.dirname(__file__), "data/figure4/data")
    )
    sort_dict_list = sorted(
        dict_list, key=lambda x: x.get("write_current").flatten()[0]
    )
    plot_enable_write_sweep_multiple(
        axs["B"],
        sort_dict_list,
        show_colorbar=False,
        range=slice(0, len(sort_dict_list) // 2),

    )
    plot_enable_write_sweep_multiple(
        axs["C"],
        sort_dict_list,
        show_colorbar=True,
        range=slice(len(sort_dict_list) // 2, len(sort_dict_list)),
    )
    axs["B"].set_xlabel("Enable Write Current [$\mu$A]")
    axs["C"].set_xlabel("Enable Write Current [$\mu$A]")
    axs["B"].set_ylabel("Bit Error Rate")
    plt.show()


if __name__ == "__main__":
    main()
