
from typing import Literal, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LogNorm

from analysis.cell_utils import (
    convert_cell_to_coordinates,
    initialize_dict,
    process_cell,
)
from analysis.constants import CELLS
from analysis.data_processing import (
    filter_first,
    get_total_switches_norm,
)


def build_array(
    data_dict: dict, parameter_z: Literal["total_switches_norm"]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if data_dict.get("total_switches_norm") is None:
        data_dict["total_switches_norm"] = get_total_switches_norm(data_dict)
    x: np.ndarray = data_dict.get("x")[0][:, 0] * 1e6
    y: np.ndarray = data_dict.get("y")[0][:, 0] * 1e6
    z: np.ndarray = data_dict.get(parameter_z)

    xlength: int = filter_first(data_dict.get("sweep_x_len", len(x)))
    ylength: int = filter_first(data_dict.get("sweep_y_len", len(y)))

    # X, Y reversed in reshape
    zarray = z.reshape((ylength, xlength), order="F")
    return x, y, zarray


def plot_parameter_array(
    ax: Axes,
    xloc: np.ndarray,
    yloc: np.ndarray,
    parameter_array: np.ndarray,
    title: str = None,
    log: bool = False,
    cmap: plt.cm = None,
) -> Axes:
    if cmap is None:
        cmap = plt.get_cmap("viridis")


    if log:
        ax.matshow(
            parameter_array,
            cmap=cmap,
            norm=LogNorm(vmin=np.min(parameter_array), vmax=np.max(parameter_array)),
        )
    else:
        ax.matshow(parameter_array, cmap=cmap)

    if title:
        ax.set_title(title)
    ax.set_xticks(range(4), ["A", "B", "C", "D"])
    ax.set_yticks(range(4), ["1", "2", "3", "4"])
    ax.tick_params(axis="both", length=0)
    return ax



def plot_ber_grid(ax: plt.Axes):
    ARRAY_SIZE = (4, 4)
    param_dict = initialize_dict(ARRAY_SIZE)
    xloc_list = []
    yloc_list = []
    for c in CELLS:
        xloc, yloc = convert_cell_to_coordinates(c)
        param_dict = process_cell(CELLS[c], param_dict, xloc, yloc)
        xloc_list.append(xloc)
        yloc_list.append(yloc)

    plot_parameter_array(
        ax,
        xloc_list,
        yloc_list,
        param_dict["bit_error_rate"],
        log=True,
        cmap=plt.get_cmap("Blues").reversed(),
    )

    ax.xaxis.set_label_position("bottom")
    ax.xaxis.set_ticks_position("bottom")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    cax = ax.inset_axes([1.10, 0, 0.1, 1])
    fig = plt.gcf()
    cbar = fig.colorbar(
        ax.get_children()[0], cax=cax, orientation="vertical", label="minimum BER"
    )

    return ax
