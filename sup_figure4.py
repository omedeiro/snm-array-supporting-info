from nmem.analysis.analysis import import_directory, plot_read_sweep_array
from nmem.analysis.write_current_sweep_operation_v2 import plot_enable_sweep
import matplotlib.pyplot as plt
import os


def plot_write_current_sweep(
    ax: plt.Axes, dict_list: list[dict[str, list[float]]]
) -> plt.Axes:
    plot_read_sweep_array(
        ax, dict_list, "bit_error_rate", "write_current", add_errorbar=False
    )
    ax.set_xlabel("Read Current [$\mu$A]")
    ax.set_ylabel("Bit Error Rate")
    # ax.legend(
    #     frameon=False, bbox_to_anchor=(1.1, 1), loc="upper left", title="Write Current"
    # )

    return ax


def main():
    fig, axs = plt.subplot_mosaic("BC", figsize=(180 / 25.4, 90 / 25.4))
    write_current_sweep = import_directory(
        "/home/omedeiro/nmem/src/nmem/analysis/read_current_sweep_write_current2/write_current_sweep_C3",
    )
    # plot_write_current_sweep(axs["A"], write_current_sweep)
    # axs["n"].axes.set_visible(False)
    # # ax = axs["A"]
    dict_list = import_directory(
        os.path.join(os.path.dirname(__file__), "enable_write_current_sweep/data")
    )
    sort_dict_list = sorted(
        dict_list, key=lambda x: x.get("write_current").flatten()[0]
    )
    plot_enable_sweep(
        axs["B"],
        sort_dict_list,
        range=slice(0, len(sort_dict_list) // 2),
        add_errorbar=False,
        add_colorbar=False,
    )
    plot_enable_sweep(
        axs["C"],
        sort_dict_list,
        range=slice(len(sort_dict_list) // 2, len(sort_dict_list)),
        add_errorbar=False,
        add_colorbar=True,
    )
    # plt.savefig("sup_full_param_sweeps.pdf", bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
