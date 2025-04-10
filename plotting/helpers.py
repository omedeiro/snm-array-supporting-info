from typing import Dict

import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.pyplot import Axes
from matplotlib.ticker import MultipleLocator

from analysis.calculations import (
    polygon_inverting,
    polygon_nominal,
)
from analysis.data_processing import (
    get_bit_error_rate,
    get_enable_current_sweep,
)
from plotting.style import CMAP


def plot_fill_between(ax: Axes, data_dict: Dict, fill_color: str) -> Axes:
    # fill the area between 0.5 and the curve
    enable_write_currents = get_enable_current_sweep(data_dict)
    bit_error_rate = get_bit_error_rate(data_dict)
    verts = polygon_nominal(enable_write_currents, bit_error_rate)
    poly = PolyCollection([verts], facecolors=fill_color, alpha=0.3, edgecolors="k")
    ax.add_collection(poly)
    verts = polygon_inverting(enable_write_currents, bit_error_rate)
    poly = PolyCollection([verts], facecolors=fill_color, alpha=0.3, edgecolors="k")
    ax.add_collection(poly)

    return ax


def plot_fill_between_array(ax: Axes, dict_list: list[dict]) -> Axes:
    colors = CMAP(np.linspace(0.1, 1, len(dict_list)))
    for i, data_dict in enumerate(dict_list):
        plot_fill_between(ax, data_dict, colors[i])
    return ax


def set_ber_ticks(ax: Axes) -> Axes:
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    return ax
