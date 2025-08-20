"""
Basic simulation example for magnet-sim.

This example demonstrates how to run a simple single-circuit simulation
with PID control using the magnet-sim package.
"""

import os
import numpy as np
import pandas as pd
from magnet_sim import simulate_magnetically_coupled_rl
from magnet_sim.utils import plot_magnetically_coupled_results

def create_sample_data():
    """Create sample data files for the simulation."""
    
    # Create resistance data
    current = np.linspace(0, 1000, 100)
    resistance = 0.001 + 0.0001 * current  # Linear resistance increase
    
    resistance_df = pd.DataFrame({
        'current': current,
        'resistance': resistance
    })
    resistance_df.to_csv('data/resistance_circuit.csv', index=False)
    
    # Create inductance matrix (single circuit)
    inductance_matrix = np.array([[0.001]])  # 1 mH self-inductance
    pd.DataFrame(inductance_matrix).to_csv('data/inductance_matrix.csv', header=False, index=False)
    
    # Create target current profile
    time = np.linspace(0, 100, 1000)
    target_current = np.where(time < 50, 
                             100 * (1 - np.exp(-time/10)),  # Rising exponential
                             100 * np.exp(-(time-50)/20))   # Falling exponential
    
    input_df = pd.DataFrame({
        'time': time,
        'current1': target_current
    })
    input_df.to_csv('data/inputs_circuits_voltages.csv', index=False)
    
    print("Sample data files created in 'data/' directory")

def main():
    """Run the basic simulation example."""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Create sample data
    create_sample_data()
    
    # Simulation parameters
    resistance_csvs = ['data/resistance_circuit.csv']
    inputs_csv = 'data/inputs_circuits_voltages.csv'
    inductance_csv = 'data/inductance_matrix.csv'
    n_circuits = 1
    t_span = (0, 100)
    initial_currents = [0.0]
    control_mode = 'pid'
    
    print("Running simulation...")
    
    # Run simulation
    results = simulate_magnetically_coupled_rl(
        resistance_csvs=resistance_csvs,
        inputs_csv=inputs_csv,
        inductance_csv=inductance_csv,
        n_circuits=n_circuits,
        t_span=t_span,
        initial_currents=initial_currents,
        control_mode=control_mode
    )
    
    print("Simulation completed!")
    
    # Plot results
    plot_magnetically_coupled_results(
        results=results,
        experiments=None,
        t_start=0,
        t_end=100,
        title_suffix="(Basic Example)",
        save=False
    )
    
    # Print some basic statistics
    final_current = results['individual_currents'][0][-1]
    max_voltage = max(results['voltages'][0])
    min_voltage = min(results['voltages'][0])
    
    print(f"\n=== SIMULATION SUMMARY ===")
    print(f"Final current: {final_current:.3f} A")
    print(f"Maximum voltage: {max_voltage:.3f} V")
    print(f"Minimum voltage: {min_voltage:.3f} V")
    print(f"Simulation time span: {t_span[0]:.1f} - {t_span[1]:.1f} s")
    print(f"Number of time points: {len(results['times'])}")

if __name__ == "__main__":
    main()