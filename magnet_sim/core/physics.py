"""
Physics models for magnetically coupled RL circuits.
"""

import numpy as np
from typing import List, Optional


def magnetically_coupled_rl_system(
    t: float, 
    currents: List[float], 
    L_matrix: np.ndarray, 
    R_funcs: List[callable], 
    n_circuits: int, 
    voltage_funcs: Optional[List[callable]] = None, 
    pid_controllers: Optional[List] = None
) -> List[float]:
    """
    True physics model of magnetically coupled RL circuits.

    System of equations: U_i = R_i(I_i) * I_i + Σ L(i,j) * dI_j/dt

    Rearranged to: [L] * d[I]/dt = [U] - [R(I)] * [I]
    So: d[I]/dt = [L]^(-1) * ([U] - [R(I)] * [I])

    Parameters
    ----------
    t : float
        Current time
    currents : List[float]
        Current state vector [I1, I2, ..., IN]
    L_matrix : np.ndarray
        Inductance matrix (N x N)
    R_funcs : List[callable]
        List of resistance functions
    n_circuits : int
        Number of circuits
    voltage_funcs : Optional[List[callable]]
        Voltage functions (if voltage mode)
    pid_controllers : Optional[List]
        PID controllers (if PID mode)

    Returns
    -------
    List[float]
        derivatives: dI/dt vector
    """
    currents = np.array(currents)

    # Calculate individual resistances: R_i(I_i)
    resistances = np.zeros(n_circuits)
    if len(R_funcs) == n_circuits:
        # Individual resistance function for each circuit
        for i in range(n_circuits):
            resistances[i] = R_funcs[i](abs(currents[i]))
    else:
        raise ValueError(
            f"R_funcs must have 1 or {n_circuits} functions, got {len(R_funcs)}"
        )

    # Calculate voltage drops due to resistance: R_i(I_i) * I_i
    resistance_drops = resistances * currents

    # Determine applied voltages U_i based on control mode
    voltages = np.zeros(n_circuits)

    if pid_controllers is not None and len(pid_controllers) == n_circuits:
        # PID mode: controllers determine voltages to achieve target currents
        for i, (current, pid) in enumerate(zip(currents, pid_controllers)):
            voltage, _ = pid.compute(current, t)
            voltages[i] = voltage

    elif voltage_funcs is not None and len(voltage_funcs) == n_circuits:
        # Voltage mode: direct voltage specification
        for i, v_func in enumerate(voltage_funcs):
            voltages[i] = v_func(t)

    else:
        # No control mode: all voltages are zero
        voltages = np.zeros(n_circuits)

    # Calculate net voltages for inductive terms: U_i - R_i(I_i) * I_i
    net_voltages = voltages - resistance_drops

    # Solve the inductance equation: [L] * d[I]/dt = [U_net]
    # d[I]/dt = [L]^(-1) * [U_net]
    try:
        di_dt = np.linalg.solve(L_matrix, net_voltages)
    except np.linalg.LinAlgError:
        # Handle singular matrix (shouldn't happen with proper inductance matrix)
        print("Warning: Singular inductance matrix encountered. Using pseudo-inverse.")
        di_dt = np.linalg.pinv(L_matrix) @ net_voltages

    return di_dt.tolist()