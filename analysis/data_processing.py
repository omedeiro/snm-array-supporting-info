import collections
import os
from typing import Literal, Tuple

import ltspice
import numpy as np

from .calculations import calculate_channel_temperature, safe_max, safe_min
from .circuit_utils import (
    get_current_or_voltage,
    get_ltsp_ber,
    get_ltsp_prob,
)
from .constants import (
    CELLS,
    CRITICAL_TEMP,
    SUBSTRATE_TEMP,
)


def process_read_data(ltsp: ltspice.Ltspice) -> dict:
    num_cases = ltsp.case_count

    read_current = np.zeros(num_cases)
    enable_read_current = np.zeros(num_cases)
    enable_write_current = np.zeros(num_cases)
    write_current = np.zeros(num_cases)
    persistent_current = np.zeros(num_cases)
    write_one_voltage = np.zeros(num_cases)
    write_zero_voltage = np.zeros(num_cases)
    read_zero_voltage = np.zeros(num_cases)
    read_one_voltage = np.zeros(num_cases)
    read_margin = np.zeros(num_cases)
    bit_error_rate = np.zeros(num_cases)
    switching_probability = np.zeros(num_cases)

    time_windows = {
        "persistent_current": (1.5e-7, 2e-7),
        "write_one": (1e-7, 1.5e-7),
        "write_zero": (5e-7, 5.5e-7),
        "read_one": (2e-7, 2.5e-7),
        "read_zero": (4e-7, 4.5e-7),
        "enable_write": (1e-7, 1.5e-7),
    }
    data_dict = {}
    for i in range(num_cases):
        time = ltsp.get_time(i)

        enable_current = ltsp.get_data("I(R1)", i) * 1e6
        channel_current = ltsp.get_data("I(R2)", i) * 1e6
        right_branch_current = ltsp.get_data("Ix(HR:drain)", i) * 1e6
        left_branch_current = ltsp.get_data("Ix(HL:drain)", i) * 1e6
        left_critical_current = get_current_or_voltage(ltsp, "ichl", i)
        right_critical_current = get_current_or_voltage(ltsp, "ichr", i)
        left_retrapping_current = get_current_or_voltage(ltsp, "irhl", i)
        right_retrapping_current = get_current_or_voltage(ltsp, "irhr", i)
        output_voltage = ltsp.get_data("V(out)", i)
        masks = {
            key: (time > start) & (time < end)
            for key, (start, end) in time_windows.items()
        }

        persistent_current[i] = safe_max(
            right_branch_current, masks["persistent_current"]
        )
        write_current[i] = safe_max(channel_current, masks["write_one"])
        read_current[i] = safe_max(channel_current, masks["read_one"])
        enable_read_current[i] = safe_max(enable_current, masks["read_one"])
        enable_write_current[i] = safe_max(enable_current, masks["enable_write"])
        write_one_voltage[i] = safe_max(output_voltage, masks["write_one"])
        write_zero_voltage[i] = safe_min(output_voltage, masks["write_zero"])
        read_zero_voltage[i] = safe_max(output_voltage, masks["read_zero"])
        read_one_voltage[i] = safe_max(output_voltage, masks["read_one"])
        read_margin[i] = read_zero_voltage[i] - read_one_voltage[i]
        bit_error_rate[i] = get_ltsp_ber(
            read_zero_voltage[i], read_one_voltage[i]
        )
        switching_probability[i] = get_ltsp_prob(
            read_zero_voltage[i], read_one_voltage[i]
        )
        data_dict[i] = {
            "time": time,
            "tran_enable_current": enable_current,
            "tran_channel_current": channel_current,
            "tran_right_branch_current": right_branch_current,
            "tran_left_branch_current": left_branch_current,
            "tran_left_critical_current": left_critical_current,
            "tran_right_critical_current": right_critical_current,
            "tran_left_retrapping_current": left_retrapping_current,
            "tran_right_retrapping_current": right_retrapping_current,
            "tran_output_voltage": output_voltage,
            "write_current": write_current,
            "read_current": read_current,
            "enable_write_current": enable_write_current,
            "enable_read_current": enable_read_current,
            "read_zero_voltage": read_zero_voltage,
            "read_one_voltage": read_one_voltage,
            "write_one_voltage": write_one_voltage,
            "write_zero_voltage": write_zero_voltage,
            "persistent_current": persistent_current,
            "case_count": ltsp.case_count,
            "read_margin": read_margin,
            "bit_error_rate": bit_error_rate,
            "switching_probability": switching_probability,
        }
    return data_dict



def get_enable_current_sweep(data_dict: dict) -> np.ndarray:

    enable_current_array: np.ndarray = data_dict.get("x")[:, :, 0].flatten() * 1e6
    if len(enable_current_array) == 1:
        enable_current_array = data_dict.get("x")[:, 0].flatten() * 1e6

    if enable_current_array[0] == enable_current_array[1]:
        enable_current_array = data_dict.get("y")[:, :, 0].flatten() * 1e6

    return enable_current_array


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



def get_total_switches_norm(data_dict: dict) -> np.ndarray:
    num_meas = data_dict.get("num_meas")[0][0]
    w0r1 = data_dict.get("write_0_read_1").flatten()
    w1r0 = num_meas - data_dict.get("write_1_read_0").flatten()
    total_switches_norm = (w0r1 + w1r0) / (num_meas * 2)
    return total_switches_norm


def get_current_cell(data_dict: dict) -> str:
    cell = filter_first(data_dict.get("cell"))
    if cell is None:
        cell = filter_first(data_dict.get("sample_name"))[-2:]
    return cell

def filter_first(value) -> any:
    if isinstance(value, collections.abc.Iterable) and not isinstance(
        value, (str, bytes)
    ):
        return np.asarray(value).flatten()[0]
    return value

def get_channel_temperature(
    data_dict: dict, operation: Literal["read", "write"]
) -> float:
    if operation == "read":
        enable_current = get_enable_read_current(data_dict)
    elif operation == "write":
        enable_current = get_enable_write_current(data_dict)

    max_enable_current = get_max_enable_current(data_dict)

    channel_temp = calculate_channel_temperature(
        CRITICAL_TEMP, SUBSTRATE_TEMP, enable_current, max_enable_current
    )
    return channel_temp


def get_channel_temperature_sweep(data_dict: dict) -> np.ndarray:
    enable_currents = get_enable_current_sweep(data_dict)

    max_enable_current = get_max_enable_current(data_dict)
    channel_temps = calculate_channel_temperature(
        CRITICAL_TEMP, SUBSTRATE_TEMP, enable_currents, max_enable_current
    )
    return channel_temps


def get_bit_error_rate(data_dict: dict) -> np.ndarray:
    return data_dict.get("bit_error_rate").flatten()


def get_critical_current_heater_off(data_dict: dict) -> np.ndarray:
    cell = get_current_cell(data_dict)
    switching_current_heater_off = CELLS[cell]["max_critical_current"] * 1e6
    return switching_current_heater_off


def get_read_current(data_dict: dict) -> float:
    if data_dict.get("read_current").shape[1] == 1:
        return filter_first(data_dict.get("read_current")) * 1e6

def get_fitting_points(
    x: np.ndarray, y: np.ndarray, ztotal: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    with np.errstate(invalid='ignore'):  # Suppress warnings for NaN comparisons
        valid_mask = ~np.isnan(ztotal)
        ztotal_filtered = np.where(valid_mask, ztotal, -np.inf)  # Replace NaNs with -inf for comparison
        mid_idx = np.where(ztotal_filtered > np.nanmax(ztotal_filtered, axis=0) / 2)
    xfit, xfit_idx = np.unique(x[mid_idx[1]], return_index=True)
    yfit = y[mid_idx[0]][xfit_idx]
    return xfit, yfit


def get_step_parameter(data_dict: dict) -> str:
    keys = [
        "write_current",
        "read_current",
        "enable_write_current",
        "enable_read_current",
    ]
    for key in keys:
        data = data_dict[key]
        if data[0] != data[1]:
            return key
    return None


def get_file_names(file_path: str) -> list:
    files = os.listdir(file_path)
    files = [file for file in files if file.endswith(".mat")]
    return files






def get_enable_read_current(data_dict: dict) -> float:
    return filter_first(data_dict.get("enable_read_current")) * 1e6


def get_enable_write_current(data_dict: dict) -> float:
    return filter_first(data_dict.get("enable_write_current")) * 1e6


def get_max_enable_current(data_dict: dict) -> float:
    cell = get_current_cell(data_dict)
    return CELLS[cell]["x_intercept"]



def get_read_width(data_dict: dict) -> float:
    return filter_first(data_dict.get("read_width"))


def get_write_width(data_dict: dict) -> float:
    return filter_first(data_dict.get("write_width"))


def get_write_currents(data_dict: dict) -> np.ndarray:
    write_currents = data_dict.get("write_current").flatten() * 1e6
    return write_currents


def get_read_currents(data_dict: dict) -> np.ndarray:
    read_currents = data_dict.get("y")[:, :, 0] * 1e6
    return read_currents.flatten()


def get_write_current(data_dict: dict) -> float:
    if data_dict.get("write_current").shape[1] == 1:
        return filter_first(data_dict.get("write_current")) * 1e6
    if data_dict.get("write_current").shape[1] > 1:
        return data_dict.get("write_current")[0, 0] * 1e6


def get_voltage_trace_data(
    data_dict: dict,
    trace_name: Literal["trace_chan_in", "trace_chan_out", "trace_enab"],
    trace_index: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    if data_dict.get(trace_name).ndim == 2:
        x = data_dict[trace_name][0] * 1e6
        y = data_dict[trace_name][1] * 1e3
    else:
        x = data_dict[trace_name][0][:, trace_index] * 1e6
        y = data_dict[trace_name][1][:, trace_index] * 1e3
    return x, y

