"""
Data loading utilities for circuit simulation.
"""

import numpy as np
import pandas as pd
from scipy import interpolate
from typing import List, Tuple, Union


def load_inductance_matrix(inductance_csv: str, n_circuits: int) -> np.ndarray:
    """
    Load inductance matrix from CSV file.

    Parameters
    ----------
    inductance_csv : str
        CSV file with inductance matrix
    n_circuits : int
        Number of circuits to validate matrix size

    Returns
    -------
    np.ndarray
        Inductance matrix of shape (n_circuits, n_circuits)

    Notes
    -----
    Expected CSV format (no headers):
    L11,L12,L13,...,L1N
    L21,L22,L23,...,L2N
    L31,L32,L33,...,L3N
    ...
    LN1,LN2,LN3,...,LNN

    Where Lij is the mutual inductance between circuit i and circuit j
    (Lii are self-inductances, Lij=Lji for i≠j)
    """
    try:
        # Load without header, assuming pure matrix format
        L_matrix = pd.read_csv(inductance_csv, header=None, sep=',').values

        # Validate matrix dimensions
        if L_matrix.shape != (n_circuits, n_circuits):
            raise ValueError(
                f"Inductance matrix must be {n_circuits}x{n_circuits}, "
                f"got {L_matrix.shape[0]}x{L_matrix.shape[1]}"
            )

        # Validate symmetry (mutual inductances should be symmetric)
        if not np.allclose(L_matrix, L_matrix.T, rtol=1e-10):
            print(
                "Warning: Inductance matrix is not symmetric. Enforcing symmetry by averaging."
            )
            L_matrix = (L_matrix + L_matrix.T) / 2

        # Validate positive definiteness (for physical realizability)
        eigenvals = np.linalg.eigvals(L_matrix)
        if np.any(eigenvals <= 0):
            print(
                "Warning: Inductance matrix has non-positive eigenvalues. "
                "This may indicate an unphysical inductance matrix."
            )

        print(
            f"Loaded {n_circuits}x{n_circuits} inductance matrix from {inductance_csv}"
        )
        print("Inductance matrix (H):")
        print(L_matrix)

        return L_matrix

    except Exception as e:
        raise ValueError(f"Error loading inductance matrix from {inductance_csv}: {e}")


def load_resistance_data(csv_files: Union[str, List[str]]) -> List[callable]:
    """
    Load resistance data for multiple circuits.

    Parameters
    ----------
    csv_files : Union[str, List[str]]
        List of CSV file paths or single file path
        If single file, same resistance function used for all circuits
        If list, each file should have columns 'current' and 'resistance'

    Returns
    -------
    List[callable]
        List of interpolation functions, one per circuit
    """
    if isinstance(csv_files, str):
        # Single file - use same resistance for all circuits
        csv_files = [csv_files]

    R_funcs = []

    for i, csv_file in enumerate(csv_files):
        try:
            data = pd.read_csv(csv_file)

            # Check required columns
            if "current" not in data.columns or "resistance" not in data.columns:
                raise ValueError(
                    f"CSV file {csv_file} must have 'current' and 'resistance' columns"
                )

            current_values = data["current"].values
            resistance_values = data["resistance"].values

            # Create interpolation function
            R_func = interpolate.interp1d(
                current_values,
                resistance_values,
                kind="linear",
                bounds_error=False,
                fill_value=(resistance_values[0], resistance_values[-1]),
            )

            R_funcs.append(R_func)
            print(f"Loaded resistance data for circuit {i+1} from {csv_file}")

        except Exception as e:
            raise ValueError(f"Error loading resistance data from {csv_file}: {e}")

    return R_funcs


def load_electrical_inputs(
    inputs_csv: str, 
    n_circuits: int, 
    input_type: str = "target"
) -> Tuple[List[callable], np.ndarray, List[np.ndarray]]:
    """
    Load electrical inputs for all circuits from a single CSV file.

    Parameters
    ----------
    inputs_csv : str
        CSV file path with electrical inputs for all circuits
    n_circuits : int
        Number of circuits
    input_type : str
        'target' for target currents (PID mode) or 'voltage' for applied voltages

    Returns
    -------
    Tuple[List[callable], np.ndarray, List[np.ndarray]]
        List of interpolation functions, times array, and raw values array

    Notes
    -----
    Expected CSV format:
    For target currents (PID): time,current1,current2,current3,...,currentN
    For voltages: time,voltage1,voltage2,voltage3,...,voltageN
    """
    print("Loading electrical inputs from CSV:", inputs_csv)
    data = pd.read_csv(inputs_csv)
    print("Available columns:", data.keys().tolist(), flush=True)

    # Check for time column
    if "time" not in data.columns:
        raise ValueError("Required column 'time' not found in the inputs CSV")

    # Determine column prefix based on input type
    if input_type == "pid":
        prefix = "current"
    elif input_type == "voltage":
        prefix = "voltage"
    else:
        raise ValueError("input_type must be 'pid' or 'voltage'")

    # Check for input columns
    input_columns = [f"{prefix}{i+1}" for i in range(n_circuits)]
    missing_cols = [col for col in input_columns if col not in data.columns]
    if missing_cols:
        available_cols = [col for col in data.columns if col.startswith(prefix)]
        raise ValueError(
            f"Missing {input_type} columns: {missing_cols}. "
            f"Available {prefix} columns: {available_cols}"
        )

    # Extract data
    times = data["time"].values
    input_values = []
    input_funcs = []

    for i in range(n_circuits):
        col_name = f"{prefix}{i+1}"
        values = data[col_name].values
        input_values.append(values)

        # Create interpolation function
        input_func = interpolate.interp1d(
            times,
            values,
            kind="linear",
            bounds_error=False,
            fill_value=(values[0], values[-1]),
        )
        input_funcs.append(input_func)

    print(f"Loaded {input_type} data for {n_circuits} circuits from {inputs_csv}")
    return input_funcs, times, input_values


def load_electrical_outputs(
    outputs_csv: str, 
    n_circuits: int, 
    output_type: str = "target"
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Load electrical outputs for comparison with simulation results.

    Parameters
    ----------
    outputs_csv : str
        CSV file path with electrical outputs
    n_circuits : int
        Number of circuits
    output_type : str
        'target' for target outputs or 'voltage' for voltage outputs

    Returns
    -------
    Tuple[np.ndarray, List[np.ndarray]]
        Times array and list of output values arrays
    """
    print("Loading electrical outputs from CSV:", outputs_csv, output_type)
    data = pd.read_csv(outputs_csv)
    print("Available columns:", data.keys().tolist(), flush=True)

    # Check for time column
    if "time" not in data.columns:
        raise ValueError("Required column 'time' not found in the outputs CSV")

    # Determine column prefix based on output type
    if output_type == "target":
        prefix = "voltage"
    elif output_type == "voltage":
        prefix = "current"
    else:
        raise ValueError("output_type must be 'target' or 'voltage'")

    # Check for output columns
    output_columns = [f"{prefix}{i+1}" for i in range(n_circuits)]
    print('output_columns:', output_columns)
    missing_cols = [col for col in output_columns if col not in data.columns]
    if missing_cols:
        available_cols = [col for col in data.columns if col.startswith(prefix)]
        raise ValueError(
            f"Missing {output_type} columns: {missing_cols}. "
            f"Available {prefix} columns: {available_cols}"
        )

    # Extract data
    times = data["time"].values
    output_values = []

    for i in range(n_circuits):
        col_name = f"{prefix}{i+1}"
        values = data[col_name].values
        output_values.append(values)

    print(f"Loaded {output_type} data for {n_circuits} circuits from {outputs_csv}")
    return times, output_values