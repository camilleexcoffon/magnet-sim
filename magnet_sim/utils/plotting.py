"""
Plotting utilities for circuit simulation results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
from typing import Dict, Any, Optional


def plot_magnetically_coupled_results(
    results: Dict[str, Any], 
    experiments: Optional[Dict[str, Any]] = None, 
    t_start: float = 0, 
    t_end: float = 100, 
    title_suffix: str = "", 
    save: bool = False
) -> None:
    """
    Plot simulation results for magnetically coupled RL circuits.
    
    Parameters
    ----------
    results : Dict[str, Any]
        Simulation results dictionary
    experiments : Optional[Dict[str, Any]]
        Experimental data for comparison
    t_start : float
        Start time for plotting
    t_end : float
        End time for plotting
    title_suffix : str
        Suffix for plot titles
    save : bool
        Whether to save the plot
    """
    times = results["times"]
    i_total = results["i_total"]
    individual_currents = results["individual_currents"]
    voltages = results["voltages"]
    inductive_voltages = results["inductive_voltages"]
    individual_resistances = results["individual_resistances"]
    control_mode = results["control_mode"]
    n_circuits = results["n_circuits"]
    L_matrix = results["L_matrix"]

    # Determine number of subplots
    if control_mode == "pid":
        n_plots = 4  
        fig_height = 10
    else:
        n_plots = 4  
        fig_height = 10

    plt.figure(figsize=(15, fig_height))
    plot_idx = 1

    # Input profiles from CSV
    ax1 = plt.subplot(n_plots, 1, plot_idx)
    ax1.set_xlim(t_start, t_end)
    colors = plt.cm.tab10(np.linspace(0, 1, n_circuits))

    input_type = "Target Current" if control_mode == "pid" else "Applied Voltage"
    mask = (results["profile_times"] >= t_start) & (results["profile_times"] <= t_end)
    
    for i in range(n_circuits):  
        inputs = np.array(results["input_values"][i])
        plt.plot(
            np.array(results["profile_times"])[mask],
            inputs[mask],
            "--",
            color=colors[i],
            label=f"Circuit {i+1} {input_type}",
        )

    if control_mode == "pid":
        # Current results
        for i in range(n_circuits):
            mask1 = (times >= t_start) & (times <= t_end)
            setpoints = np.array(results["setpoints"][i])
            plt.plot(
                np.array(times)[mask1],
                setpoints[mask1],
                "o",
                color=colors[i],
                label=f"Circuit {i+1}",
                markevery=100,
            )
        plt.ylabel("Current (A)")
    else:
        plt.ylabel("Voltage (V)")

    plt.title(f"{input_type} Profiles {title_suffix}")
    plt.grid(True)
    plt.legend(loc='upper left')
    plot_idx += 1

    # Individual currents/voltages plot
    ax2 = plt.subplot(n_plots, 1, plot_idx, sharex=ax1)
    
    for i in range(n_circuits):
        if control_mode == "pid":
            plt.plot(
                times, 
                results["voltages"][i],
                "--",
                color=colors[i],
                alpha=0.7,
                label=f"Voltage {i+1}",
            )
        else:
            plt.plot(
                times,
                individual_currents[i],
                "-",
                color=colors[i],
                label=f"Circuit {i+1} Current",
            )
    
    if experiments:
        legend = "exp Circuit"
        if control_mode == "pid":
            legend = "exp Voltage"
        for i in range(n_circuits):    
            plt.plot(
                np.array(experiments["profile_times"])[mask],
                np.array(experiments["output_values"][i])[mask],
                "o",
                color=colors[i],  
                linestyle='None',
                markevery=10,
                label=f"{legend} {i+1}"   
            )

    plt.title(f"Individual Circuit Currents {title_suffix}")
    plt.ylabel("Current (A)")
    if control_mode == "pid":
        plt.title(f"Individual Applied Voltages {title_suffix}")
        plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.legend(loc='upper left')
    plot_idx += 1

    # Individual resistances plot
    ax3 = plt.subplot(n_plots, 1, plot_idx, sharex=ax1)
    for i in range(n_circuits):
        plt.plot(
            times,
            individual_resistances[i],
            "-",
            color=colors[i],
            label=f"Circuit {i+1} Resistance",
        )

    plt.title(f"Individual Resistances $R_i(I_i)$ {title_suffix}")
    plt.ylabel("Resistance ($\\Omega$)")
    plt.grid(True)
    plt.legend(loc='upper left')
    plot_idx += 1

    # Error calculation
    ax4 = plt.subplot(n_plots, 1, plot_idx, sharex=ax1)
    
    for i in range(n_circuits):
        if control_mode == 'pid':
            interp_setpoint = interpolate.interp1d(
                times, results["setpoints"][i], 
                kind='linear', bounds_error=False
            )
            cmp_setpoint = interp_setpoint(results["profile_times"])
            error_current = abs(results["input_values"][i] - cmp_setpoint) / np.max(results["setpoints"][i]) * 100
            
            if experiments:
                interp_voltages = interpolate.interp1d(
                    times, results["voltages"][i], 
                    kind='linear', bounds_error=False
                )
                cmp_voltage = interp_voltages(experiments["profile_times"])
                error_voltage = abs((cmp_voltage - experiments["output_values"][i])) / np.max(results["voltages"][i]) * 100
                
                plt.plot(
                    results["profile_times"],
                    error_voltage,
                    '-',
                    color=colors[i],
                    label=f'Voltage {i+1}',
                )
            label = "Error of current and voltage"
        else: 
            if experiments:
                interp_currents = interpolate.interp1d(
                    times, individual_currents[i], 
                    kind='linear', bounds_error=False
                )
                cmp_currents = interp_currents(experiments["profile_times"])
                error_current = abs(cmp_currents - experiments["output_values"][i]) / np.max(experiments["output_values"][i]) * 100
            else:
                error_current = np.zeros_like(results["profile_times"])
            label = "Error of current"
         
        plt.plot(
            results["profile_times"],
            error_current,
            '-',
            color=colors[i],
            label=f'Current {i+1}',
        )
            
    plt.title(label)
    plt.xlabel("Time (seconds)")
    plt.ylabel('Error [%]')
    plt.grid(True)
    plt.legend(loc='upper left')

    plt.tight_layout()

    if save:
        plt.savefig("ODE/circuit")
        print("Graph saved in ODE directory")
    else:
        plt.show()

    # Print physics verification and coupling info
    print(f"\n=== PHYSICS VERIFICATION ===")
    print(f"System: U_i = R_i(I_i)×I_i + Σ L(i,j)×dI_j/dt")
    print(f"Number of circuits: {n_circuits}")
    print(f"Control mode: {control_mode}")

    print(f"\nInductance Matrix L(i,j) [H]:")
    for i in range(n_circuits):
        row_str = " ".join([f"{L_matrix[i,j]:8.4f}" for j in range(n_circuits)])
        print(f"Circuit {i+1}: [{row_str}]")

    print(f"\nSelf-inductances [H]: {[L_matrix[i,i] for i in range(n_circuits)]}")

    if n_circuits > 1:
        print(f"\nMutual inductances [H]:")
        for i in range(n_circuits):
            for j in range(i + 1, n_circuits):
                print(f"L({i+1},{j+1}) = {L_matrix[i,j]:.6f} H")

        print(f"\nCoupling coefficients k(i,j) = M(i,j)/sqrt(L(i,i)×L(j,j)):")
        for i in range(n_circuits):
            for j in range(i + 1, n_circuits):
                k_ij = L_matrix[i, j] / np.sqrt(L_matrix[i, i] * L_matrix[j, j])
                coupling_strength = (
                    "weak" if k_ij < 0.1 else "moderate" if k_ij < 0.5 else "strong"
                )
                print(f"k({i+1},{j+1}) = {k_ij:.6f} ({coupling_strength} coupling)")

    # Verify physics equation at a few time points
    print(f"\n=== EQUATION VERIFICATION (sample points) ===")
    sample_indices = [len(times) // 4, len(times) // 2, 3 * len(times) // 4]

    for idx in sample_indices:
        t = times[idx]
        print(f"\nTime t = {t:.2f}s:")

        for i in range(min(n_circuits, 3)):  # Show first 3 circuits max
            # Left side: U_i
            U_i = voltages[i][idx]

            # Right side components
            R_i = individual_resistances[i][idx]
            I_i = individual_currents[i][idx]
            resistive_term = R_i * I_i
            inductive_term = inductive_voltages[i][idx]

            total_right = resistive_term + inductive_term
            error = abs(U_i - total_right)

            print(
                f"  Circuit {i+1}: U_{i+1} = {U_i:7.3f}V | "
                f"R_{i+1}×I_{i+1} + L_terms = {resistive_term:7.3f} + {inductive_term:7.3f} = {total_right:7.3f}V | "
                f"Error = {error:.6f}V"
            )

    # Calculate tracking performance (only for PID mode)
    if control_mode == "pid" and results["setpoints"][0][0] is not None:
        print(f"\n=== PID PERFORMANCE METRICS ===")

        for i in range(n_circuits):
            avg_error = np.mean(
                [
                    abs(curr - sp)
                    for curr, sp in zip(individual_currents[i], results["setpoints"][i])
                ]
            )
            max_error = np.max(
                [
                    abs(curr - sp)
                    for curr, sp in zip(individual_currents[i], results["setpoints"][i])
                ]
            )
            print(
                f"Circuit {i+1}: Avg error = {avg_error:.4f}A, Max error = {max_error:.4f}A"
            )

        total_avg_error = np.mean(
            [abs(i - sp) for i, sp in zip(i_total, results["total_setpoint"])]
        )
        total_max_error = np.max(
            [abs(i - sp) for i, sp in zip(i_total, results["total_setpoint"])]
        )
        print(
            f"Total Current: Avg error = {total_avg_error:.4f}A, Max error = {total_max_error:.4f}A"
        )