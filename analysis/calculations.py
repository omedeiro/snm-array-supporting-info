from typing import Tuple

import numpy as np


def safe_max(arr: np.ndarray, mask: np.ndarray) -> float:
    if np.any(mask):
        return np.max(arr[mask])
    return 0


def safe_min(arr: np.ndarray, mask: np.ndarray) -> float:
    if np.any(mask):
        return np.min(arr[mask])
    return 0


def filter_plateau(
    xfit: np.ndarray, yfit: np.ndarray, plateau_height: float
) -> Tuple[np.ndarray, np.ndarray]:
    xfit = np.where(yfit < plateau_height, xfit, np.nan)
    yfit = np.where(yfit < plateau_height, yfit, np.nan)

    # Remove nans
    xfit = xfit[~np.isnan(xfit)]
    yfit = yfit[~np.isnan(yfit)]

    return xfit, yfit



def calculate_heater_power(heater_current: float, heater_resistance: float) -> float:
    return heater_current**2 * heater_resistance


def htron_critical_current(
    heater_current: float,
    slope: float,
    intercept: float,
) -> float:
    """Calculate the critical current of the device.

    Parameters
    ----------
    heater_current : float
        The current through the heater I_H.
    slope : float
        The slope of linear enable response I_C(I_H) .
    intercept : float
        The y-intercept of the linear enable response in microamps.

    Returns
    -------
    critical_current : float
        The critical current of the device in microamps.
    """
    channel_current = heater_current * slope + intercept
    return channel_current


def polygon_nominal(x: np.ndarray, y: np.ndarray) -> list:
    y = np.copy(y)
    y[y > 0.5] = 0.5
    return [(x[0], 0.5), *zip(x, y), (x[-1], 0.5)]


def polygon_inverting(x: np.ndarray, y: np.ndarray) -> list:
    y = np.copy(y)
    y[y < 0.5] = 0.5
    return [(x[0], 0.5), *zip(x, y), (x[-1], 0.5)]


def calculate_channel_temperature(
    critical_temperature: float,
    substrate_temperature: float,
    ih: float,
    ih_max: float,
) -> float:
    N = 2.0
    beta = 1.25
    if ih_max == 0:
        raise ValueError("ih_max cannot be zero to avoid division by zero.")

    channel_temperature = (critical_temperature**4 - substrate_temperature**4) * (
        (ih / ih_max) ** N
    ) + substrate_temperature**4

    channel_temperature = np.maximum(channel_temperature, 0)

    temp_channel = np.power(channel_temperature, 0.25).astype(float)
    return temp_channel


def get_bit_error_rate_args(bit_error_rate: np.ndarray) -> list:
    nominal_args = np.argwhere(bit_error_rate < 0.45)
    inverting_args = np.argwhere(bit_error_rate > 0.55)

    if len(inverting_args) > 0:
        inverting_arg1 = inverting_args[0][0]
        inverting_arg2 = inverting_args[-1][0]
    else:
        inverting_arg1 = np.nan
        inverting_arg2 = np.nan

    if len(nominal_args) > 0:
        nominal_arg1 = nominal_args[0][0]
        nominal_arg2 = nominal_args[-1][0]
    else:
        nominal_arg1 = np.nan
        nominal_arg2 = np.nan

    return nominal_arg1, nominal_arg2, inverting_arg1, inverting_arg2


