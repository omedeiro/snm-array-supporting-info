import collections
import os
from typing import Literal, Tuple

import ltspice
import numpy as np
import scipy.io as sio

from cells import CELLS

SUBSTRATE_TEMP = 1.3
CRITICAL_TEMP = 12.3
READ_XMIN = 400
READ_XMAX = 1000
IC0_C3 = 910
VOLTAGE_THRESHOLD = 2.0e-3


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



def process_cell(cell: dict, param_dict: dict, x: int, y: int) -> dict:
    param_dict["write_current"][y, x] = cell["write_current"] * 1e6
    param_dict["read_current"][y, x] = cell["read_current"] * 1e6
    param_dict["enable_write_current"][y, x] = cell["enable_write_current"] * 1e6
    param_dict["enable_read_current"][y, x] = cell["enable_read_current"] * 1e6
    param_dict["slope"][y, x] = cell["slope"]
    param_dict["y_intercept"][y, x] = cell["y_intercept"]
    param_dict["resistance"][y, x] = cell["resistance_cryo"]
    param_dict["bit_error_rate"][y, x] = cell.get("min_bit_error_rate", np.nan)
    param_dict["max_critical_current"][y, x] = (
        cell.get("max_critical_current", np.nan) * 1e6
    )
    if cell["y_intercept"] != 0:
        write_critical_current = htron_critical_current(
            cell["enable_write_current"] * 1e6, cell["slope"], cell["y_intercept"]
        )
        read_critical_current = htron_critical_current(
            cell["enable_read_current"] * 1e6, cell["slope"], cell["y_intercept"]
        )
        param_dict["x_intercept"][y, x] = -cell["y_intercept"] / cell["slope"]
        param_dict["write_current_norm"][y, x] = (
            cell["write_current"] * 1e6 / write_critical_current
        )
        param_dict["read_current_norm"][y, x] = (
            cell["read_current"] * 1e6 / read_critical_current
        )
        param_dict["enable_write_power"][y, x] = calculate_heater_power(
            cell["enable_write_current"], cell["resistance_cryo"]
        )
        param_dict["enable_write_current_norm"][y, x] = (
            cell["enable_write_current"] * 1e6 / param_dict["x_intercept"][y, x]
        )
        param_dict["enable_read_power"][y, x] = calculate_heater_power(
            cell["enable_read_current"], cell["resistance_cryo"]
        )
        param_dict["enable_read_current_norm"][y, x] = (
            cell["enable_read_current"] * 1e6 / param_dict["x_intercept"][y, x]
        )
    return param_dict


def initialize_dict(array_size: tuple) -> dict:
    return {
        "write_current": np.zeros(array_size),
        "write_current_norm": np.zeros(array_size),
        "read_current": np.zeros(array_size),
        "read_current_norm": np.zeros(array_size),
        "slope": np.zeros(array_size),
        "y_intercept": np.zeros(array_size),
        "x_intercept": np.zeros(array_size),
        "resistance": np.zeros(array_size),
        "bit_error_rate": np.zeros(array_size),
        "max_critical_current": np.zeros(array_size),
        "enable_write_current": np.zeros(array_size),
        "enable_write_current_norm": np.zeros(array_size),
        "enable_read_current": np.zeros(array_size),
        "enable_read_current_norm": np.zeros(array_size),
        "enable_write_power": np.zeros(array_size),
        "enable_read_power": np.zeros(array_size),
    }



def convert_cell_to_coordinates(cell: str) -> tuple:
    """Converts a cell name like 'A1' to coordinates (x, y)."""
    column_letter = cell[0]
    row_number = int(cell[1:]) - 1
    column_number = ord(column_letter) - ord("A")
    return column_number, row_number


def get_channel_temperature_sweep(data_dict: dict) -> np.ndarray:
    enable_currents = get_enable_current_sweep(data_dict)

    max_enable_current = get_max_enable_current(data_dict)
    channel_temps = calculate_channel_temperature(
        CRITICAL_TEMP, SUBSTRATE_TEMP, enable_currents, max_enable_current
    )
    return channel_temps


def get_critical_current_heater_off(data_dict: dict) -> np.ndarray:
    cell = get_current_cell(data_dict)
    switching_current_heater_off = CELLS[cell]["max_critical_current"] * 1e6
    return switching_current_heater_off


def get_read_current(data_dict: dict) -> float:
    if data_dict.get("read_current").shape[1] == 1:
        return filter_first(data_dict.get("read_current")) * 1e6



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


def polygon_nominal(x: np.ndarray, y: np.ndarray) -> list:
    y = np.copy(y)
    y[y > 0.5] = 0.5
    return [(x[0], 0.5), *zip(x, y), (x[-1], 0.5)]


def polygon_inverting(x: np.ndarray, y: np.ndarray) -> list:
    y = np.copy(y)
    y[y < 0.5] = 0.5
    return [(x[0], 0.5), *zip(x, y), (x[-1], 0.5)]


def save_directory_list(file_path: str, file_list: list[str]) -> None:
    with open(os.path.join(file_path, "data.txt"), "w") as f:
        for file_name in file_list:
            f.write(file_name + "\n")

    f.close()

    return


def get_bit_error_rate(data_dict: dict) -> np.ndarray:
    return data_dict.get("bit_error_rate").flatten()


def import_directory(file_path: str) -> list[dict]:
    dict_list = []
    files = get_file_names(file_path)
    files = sorted(files)
    for file in files:
        data = sio.loadmat(os.path.join(file_path, file))
        dict_list.append(data)

    save_directory_list(file_path, files)
    return dict_list


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


def get_enable_read_current(data_dict: dict) -> float:
    return filter_first(data_dict.get("enable_read_current")) * 1e6


def get_enable_write_current(data_dict: dict) -> float:
    return filter_first(data_dict.get("enable_write_current")) * 1e6


def get_max_enable_current(data_dict: dict) -> float:
    cell = get_current_cell(data_dict)
    return CELLS[cell]["x_intercept"]


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


def safe_max(arr: np.ndarray, mask: np.ndarray) -> float:
    if np.any(mask):
        return np.max(arr[mask])
    return 0


def safe_min(arr: np.ndarray, mask: np.ndarray) -> float:
    if np.any(mask):
        return np.min(arr[mask])
    return 0


def get_total_switches_norm(data_dict: dict) -> np.ndarray:
    num_meas = data_dict.get("num_meas")[0][0]
    w0r1 = data_dict.get("write_0_read_1").flatten()
    w1r0 = num_meas - data_dict.get("write_1_read_0").flatten()
    total_switches_norm = (w0r1 + w1r0) / (num_meas * 2)
    return total_switches_norm


def get_switching_probability(
    read_zero_voltage: float,
    read_one_voltage: float,
    voltage_threshold: float = VOLTAGE_THRESHOLD,
) -> float:
    switching_probability = np.where(
        (read_one_voltage > voltage_threshold)
        & (read_zero_voltage > voltage_threshold),
        1,
        0.5,
    )
    switching_probability = np.where(
        (read_one_voltage < voltage_threshold)
        & (read_zero_voltage < voltage_threshold),
        0,
        switching_probability,
    )
    return switching_probability


def get_bit_error_rate_thresh(
    read_zero_voltage: float,
    read_one_voltage: float,
    voltage_threshold: float = VOLTAGE_THRESHOLD,
) -> float:
    ber = np.where(
        (read_one_voltage < voltage_threshold)
        & (read_zero_voltage > voltage_threshold),
        1,
        0.5,
    )
    ber = np.where(
        (read_one_voltage > voltage_threshold)
        & (read_zero_voltage < voltage_threshold),
        0,
        ber,
    )
    return ber


def get_current_or_voltage(
    ltsp: ltspice.Ltspice, signal: str, case: int = 0
) -> np.ndarray:
    signal_data = ltsp.get_data(f"I({signal})", case=case)
    if signal_data is None:
        signal_data = ltsp.get_data(f"V({signal})", case=case)
    return signal_data * 1e6


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
        bit_error_rate[i] = get_bit_error_rate_thresh(
            read_zero_voltage[i], read_one_voltage[i]
        )
        switching_probability[i] = get_switching_probability(
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

