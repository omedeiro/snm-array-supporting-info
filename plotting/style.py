import os
from typing import Literal

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.axes import Axes
from matplotlib.ticker import MultipleLocator

from analysis.utils import (
    get_enable_read_current,
)

# Color palettes
CMAP = plt.get_cmap("coolwarm")
CMAP2 = plt.get_cmap("viridis")
CMAP3 = plt.get_cmap("plasma")
COLORS = [
    "#1b9e77",  # Teal green
    "#d95f02",  # Burnt orange
    "#7570b3",  # Muted blue-purple
    "#e7298a",  # Reddish pink
    "#66a61e",  # Olive green
    "#e6ab02",  # Mustard yellow
    "#a6761d",  # Brown
    "#666666",  # Dark gray
]

COLOR_CYCLER = cycler(color=COLORS)


def apply_snm_style():
    mpl.rcParams.update({
        "figure.figsize": [3.5, 3.5],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 7,
        "axes.linewidth": 0.5,
        "axes.prop_cycle": COLOR_CYCLER,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "lines.markersize": 2,
        "lines.linewidth": 1.5,
        "legend.fontsize": 5,
        "legend.frameon": False,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.minor.size": 2,
        "ytick.minor.size": 2,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
    })


def set_inter_font():
    if os.name == "nt":  # Windows
        font_path = r"C:\Users\ICE\AppData\Local\Microsoft\Windows\Fonts\Inter-VariableFont_opsz,wght.ttf"
    elif os.name == "posix":
        font_path = "/home/omedeiro/Inter-VariableFont_opsz,wght.ttf"
    else:
        font_path = None

    if font_path and os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        mpl.rcParams["font.family"] = "Inter"


def get_cmap_colors(n, cmap=CMAP, lo=0.1, hi=1.0):
    return cmap(np.linspace(lo, hi, n))

def add_colorbar(ax, values, label, cmap=CMAP, cax=None):
    if cax is None:
        cax = ax
    norm = mcolors.Normalize(vmin=min(values), vmax=max(values))
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=cax, orientation="vertical", fraction=0.05, pad=0.05)
    cbar.set_label(label)
    return cbar

def add_dict_colorbar(
    ax: plt.Axes,
    data_dict_list: list[dict],
    cbar_label: Literal["write_current", "enable_read_current"],
    cax=None,
):
    data_list = []
    for data_dict in data_dict_list:
        if cbar_label == "write_current":
            data_list += [d["write_current"] * 1e6 for d in data_dict]
            label = "Write Current [$\mu$A]"
        elif cbar_label == "enable_read_current":
            enable_read_current = [get_enable_read_current(d) for d in data_dict]
            # print(f"Enable Read Current: {enable_read_current}")
            # data_list += [enable_read_current]
            data_list = enable_read_current
            label = "Enable Read Current [$\mu$A]"

    norm = mcolors.Normalize(vmin=min(data_list), vmax=max(data_list))
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
    sm.set_array([])

    if cax is not None:
        cbar = plt.colorbar(sm, cax=cax)
    else:
        cbar = plt.colorbar(sm, ax=ax, orientation="vertical", fraction=0.05, pad=0.05)

    cbar.set_label(label)
    return cbar

def add_ber_error_band(ax: Axes, x: np.ndarray, y: np.ndarray, color=None, alpha=0.1) -> Axes:
    """
    Adds a shaded error band based on binomial uncertainty.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis to plot on.
    x : np.ndarray
        The x-values (e.g., current).
    y : np.ndarray
        The y-values (e.g., BER between 0 and 1).
    color : any
        Matplotlib color (optional).
    alpha : float
        Transparency level of the fill (default 0.1).
    """
    n = len(y)
    error = np.sqrt(y * (1 - y) / n)
    ax.fill_between(x, y - error, y + error, alpha=alpha, color=color)
    return ax
    
def set_figsize_small():
    mpl.rcParams["figure.figsize"] = [3.5, 2.5]

def set_figsize_wide():
    mpl.rcParams["figure.figsize"] = [7, 2.5]

def set_figsize_square():
    mpl.rcParams["figure.figsize"] = [3.5, 3.5]

def set_figsize_max():
    mpl.rcParams["figure.figsize"] = [7, 7]

def format_ber_axis(ax: Axes) -> Axes:
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    return ax
