
import ltspice
import numpy as np

from .constants import VOLTAGE_THRESHOLD


def get_ltsp_ber(
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

def get_ltsp_prob(
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

def get_current_or_voltage(
    ltsp: ltspice.Ltspice, signal: str, case: int = 0
) -> np.ndarray:
    signal_data = ltsp.get_data(f"I({signal})", case=case)
    if signal_data is None:
        signal_data = ltsp.get_data(f"V({signal})", case=case)
    return signal_data * 1e6
