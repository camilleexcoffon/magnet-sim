"""
Core simulation functions for magnetically coupled RL circuits.
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import List, Optional, Tuple, Dict, Any

from ..utils.data_loader import (
    load_inductance_matrix,
    load_resistance_data,
    load_electrical_inputs,
)
from .controllers import PIDController
from .physics import magnetically_coupled_rl_system


def simulate_magnetically_coupled_rl(
    resistance_csvs: List[str],
    inputs_csv: str,
    inductance_csv: str,
    n_circuits: int,
    t_span: Tuple[float, float],
    initial_currents: Optional[List[float]] = None,
    control_mode: str = "pid",
) -> Dict[str, Any]:
    """
    Simulate magnetically coupled RL circuits with true physics.

    Physics: U_i = R_i(I_i) * I_i + Σ L(i,j) * dI_j/dt

    Parameters
    ----------
    resistance_csvs : List[str]
        List of CSV files (one per circuit) or single CSV file
    inputs_csv : str
        Single CSV file with electrical inputs (targets or voltages)
    inductance_csv : str
        CSV file with NxN inductance matrix
    n_circuits : int
        Number of circuits
    t_span : Tuple[float, float]
        Time span for simulation (start, end)
    initial_currents : Optional[List[float]]
        [I1_0, I2_0, ..., IN_0] initial currents
    control_mode : str
        'pid' (current control), 'voltage' (voltage specified), or 'none' (free response)

    Returns
    -------
    Dict[str, Any]
        Dictionary containing simulation results
    """
    if n_circuits < 1:
        raise ValueError("n_circuits must be at least 1")

    # Load inductance matrix
    print('inductance_csv:', inductance_csv)
    L_matrix = load_inductance_matrix(inductance_csv, n_circuits)

    # Load resistance data
    if isinstance(resistance_csvs, str):
        R_funcs = load_resistance_data([resistance_csvs])
    elif isinstance(resistance_csvs, list):
        if len(resistance_csvs) == n_circuits:
            R_funcs = load_resistance_data(resistance_csvs)
        else:
            raise ValueError(f"resistance_csvs must have 1 or {n_circuits} files")
    else:
        raise ValueError("resistance_csvs must be a string or list of strings")

    print("Loaded resistance functions for circuits:", len(R_funcs))
    
    # Set default initial conditions
    if initial_currents is None:
        initial_currents = [0.0] * n_circuits
    elif len(initial_currents) != n_circuits:
        raise ValueError(f"initial_currents must have {n_circuits} values")

    # Initialize control variables
    pid_controllers = None
    voltage_funcs = None
    profile_times, input_values = None, None

    print("control_mode=", control_mode)

    # Setup control based on mode
    if control_mode == "pid":
        # Load target current profiles
        target_funcs, profile_times, input_values = load_electrical_inputs(
            inputs_csv, n_circuits, input_type='pid'
        )

        # Create PID controllers
        output_limits = (-100, 100000)
        pid_controllers = []
        for i in range(n_circuits):
            pid = PIDController(
                setpoint_func=target_funcs[i],
                output_limits=output_limits,
                name=f"PID{i+1}",
            )
            pid_controllers.append(pid)
    
    elif control_mode == "voltage":
        # Load voltage profiles directly
        voltage_funcs, profile_times, input_values = load_electrical_inputs(
            inputs_csv, n_circuits, input_type="voltage"
        )

    elif control_mode == "none":
        # No control - free response with zero applied voltage
        pass

    else:
        raise ValueError("control_mode must be 'pid', 'voltage', or 'none'")

    # Solve the system of ODEs
    solution = solve_ivp(
        lambda t, currents: magnetically_coupled_rl_system(
            t, currents, L_matrix, R_funcs, n_circuits, voltage_funcs, pid_controllers
        ),
        t_span,
        initial_currents,
        method="RK45",
        dense_output=True,
        rtol=1e-6,
        atol=1e-9,
        max_step=0.01,
    )

    # Extract results
    times = solution.t
    individual_currents = [solution.y[i] for i in range(n_circuits)]
    i_total = np.sum(individual_currents, axis=0)

    # Calculate voltages and setpoints for analysis
    all_voltages = []
    all_setpoints = []
    all_inductive_voltages = []

    if control_mode == "pid":
        # Reset PID controllers for post-processing
        pid_controllers_reset = []
        for i in range(n_circuits):
            target_funcs, _, _ = load_electrical_inputs(
                inputs_csv, n_circuits, input_type="pid"
            )
            pid = PIDController(
                setpoint_func=target_funcs[i],
                output_limits=(-100, 100000),
                name=f"PID{i+1}",
            )
            pid_controllers_reset.append(pid)

        # Calculate voltages and setpoints
        for i in range(n_circuits):
            voltages_i = []
            setpoints_i = []
            inductive_voltages_i = []

            for j, (t, current_i) in enumerate(zip(times, individual_currents[i])):
                # PID voltage
                v, sp = pid_controllers_reset[i].compute(current_i, t)
                voltages_i.append(v)
                setpoints_i.append(sp)

                # Resistance drop
                if len(R_funcs) == 1:
                    R_i = R_funcs[0](abs(current_i))
                else:
                    R_i = R_funcs[i](abs(current_i))

                # Inductive voltage (approximate using finite differences)
                if j > 0:
                    dt = times[j] - times[j - 1]
                    inductive_v = 0.0
                    for k in range(n_circuits):
                        di_dt = (
                            individual_currents[k][j] - individual_currents[k][j - 1]
                        ) / dt
                        inductive_v += L_matrix[i, k] * di_dt
                    inductive_voltages_i.append(inductive_v)
                else:
                    inductive_voltages_i.append(0.0)

            all_voltages.append(voltages_i)
            all_setpoints.append(setpoints_i)
            all_inductive_voltages.append(inductive_voltages_i)

    elif control_mode == "voltage":
        for i in range(n_circuits):
            voltages_i = [voltage_funcs[i](t) for t in times]
            all_voltages.append(voltages_i)
            all_setpoints.append([None] * len(times))

            # Calculate resistance drops
            inductive_voltages_i = []
            for j, (t, current_i) in enumerate(zip(times, individual_currents[i])):
                if len(R_funcs) == 1:
                    R_i = R_funcs[0](abs(current_i))
                else:
                    R_i = R_funcs[i](abs(current_i))

                # Inductive voltage
                if j > 0:
                    dt = times[j] - times[j - 1]
                    inductive_v = 0.0
                    for k in range(n_circuits):
                        di_dt = (
                            individual_currents[k][j] - individual_currents[k][j - 1]
                        ) / dt
                        inductive_v += L_matrix[i, k] * di_dt
                    inductive_voltages_i.append(inductive_v)
                else:
                    inductive_voltages_i.append(0.0)

            all_inductive_voltages.append(inductive_voltages_i)

    else:  # control_mode == 'none'
        raise RuntimeError(f"control_mode={control_mode} not supported")

    # Calculate individual resistances for plotting
    all_resistances = []
    for i in range(n_circuits):
        resistances_i = []
        for current_i in individual_currents[i]:
            if len(R_funcs) == 1:
                R_i = R_funcs[0](abs(current_i))
            else:
                R_i = R_funcs[i](abs(current_i))
            resistances_i.append(R_i)
        all_resistances.append(resistances_i)

    # Calculate total setpoint if available
    if control_mode == "pid":
        total_setpoint = [sum(setpoints) for setpoints in zip(*all_setpoints)]
    else:
        total_setpoint = [None] * len(times)

    return {
        "times": times,
        "i_total": i_total,
        "individual_currents": individual_currents,
        "voltages": all_voltages,
        "inductive_voltages": all_inductive_voltages,
        "individual_resistances": all_resistances,
        "setpoints": all_setpoints,
        "total_setpoint": total_setpoint,
        "profile_times": profile_times,
        "input_values": input_values,
        "control_mode": control_mode,
        "n_circuits": n_circuits,
        "L_matrix": L_matrix,
    }