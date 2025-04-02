import matplotlib.pyplot as plt

from analysis.file_utils import import_directory
from plotting.style import apply_snm_style, set_figsize_max
from plotting.sweeps import plot_full_grid

apply_snm_style()

def main():
    dict_list = import_directory("data/sup_figure1/")

    fig, axs = plt.subplots(
        nrows=5, ncols=5, 
        figsize=set_figsize_max(),
        sharex=True, sharey=True
    )
    plot_full_grid(axs, dict_list)
    plt.show()

if __name__ == "__main__":
    main()
