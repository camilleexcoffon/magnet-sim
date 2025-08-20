"""
Command-line interface for magnet-sim.
"""

import os
import sys
import pandas as pd
from typing import Optional

from ..utils.config import parse_arguments, validate_arguments
from ..utils.data_loader import load_electrical_inputs, load_electrical_outputs
from ..core.simulation import simulate_magnetically_coupled_rl
from ..utils.plotting import plot_magnetically_coupled_results


def main() -> int:
    """Main function for command-line interface."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validation
        try:
            validate_arguments(args)
        except (ValueError, FileNotFoundError) as e:
            print(f"Error: {e}")
            return 1
        
        # Display parameters
        print('Current working dir:', os.getcwd())
        print(f"Time span: ({args.t_start}, {args.t_end})")
        print(f"Circuits: {args.n_circuits}")
        
        # Use parameters
        cwd = os.getcwd()
        input_dir = cwd
        if args.input_dir is not None:
            input_dir = args.input_dir
            os.chdir(input_dir)
            
        t_start = args.t_start
        t_end = args.t_end
        t_span = (t_start, t_end)
        n_circuits = args.n_circuits
        resistance_csvs = args.resistance_files
        inductance_csv = args.inductance_file
        inputs_csv = args.inputs_file
        expected_currents_csv = args.expected_values
        
        if args.verbose:
            print(f"Resistance files: {resistance_csvs}")
            print(f"Inductance file: {inductance_csv}")
            print(f"Inputs file: {inputs_csv}")
            print(f"Expected currents file: {expected_currents_csv}")

        print("Configuration loaded successfully!")
        control_mode = args.mode
        print("control_mode", control_mode)
        
        # Set initial currents based on control mode
        if control_mode == 'pid':
            # Load current setpoint and interpolate at t_start for each circuit
            input_funcs, _, _ = load_electrical_inputs(inputs_csv, n_circuits, input_type="pid")
            initial_currents = [input_funcs[i](t_span[0]) for i in range(n_circuits)]
        else:
            # Load initial currents from expected values file
            if os.path.exists(expected_currents_csv):
                df = pd.read_csv(expected_currents_csv)
                index_t_start = (df["time"] - t_start).abs().argmin() 
                initial_currents = [df[f"current{i+1}"].iloc[index_t_start] for i in range(n_circuits)]
            else:
                initial_currents = [0.0] * n_circuits

        # Run simulation
        results = simulate_magnetically_coupled_rl(
            resistance_csvs,
            inputs_csv,
            inductance_csv,
            n_circuits,
            t_span,
            initial_currents=initial_currents,
            control_mode=control_mode,
        )

        # Load experimental data for comparison
        experiments = {}
        if os.path.exists(expected_currents_csv):
            if control_mode == 'pid':
                output_type = 'target'
            else:
                output_type = 'voltage'
            print("output_type", output_type)
            
            profile_times, output_values = load_electrical_outputs(
                expected_currents_csv, n_circuits, output_type=output_type
            ) 
            experiments = {
                "profile_times": profile_times,
                "output_values": output_values
            }

        # Generate plot title
        if control_mode == 'pid':
            title_suffix = "(RL Circuit, PID)"
        else:
            title_suffix = "(RL Circuit, no PID)"
            
        # Plot results
        plot_magnetically_coupled_results(
            results, experiments, t_start, t_end, title_suffix, save=args.save
        )

        # Save results to CSV (optional)
        try:
            if control_mode == 'pid':           
                data = {'time': results["profile_times"]}
                for i in range(n_circuits):
                    interpolated_voltage = pd.Series(results["voltages"][i]).interpolate().values
                    # Resample to match profile times
                    import numpy as np
                    interpolated_voltage = np.interp(
                        results["profile_times"], 
                        results["times"], 
                        results["voltages"][i]
                    )
                    data[f'voltage{i+1}'] = interpolated_voltage
                df = pd.DataFrame(data)
                output_file = 'voltage_circuit.csv'
                df.to_csv(output_file, index=False)
                print(f"Voltage data saved to {output_file}")
            else: 
                data = {'time': results["profile_times"]}
                for i in range(n_circuits):
                    import numpy as np
                    interpolated_current = np.interp(
                        results["profile_times"], 
                        results["times"], 
                        results["individual_currents"][i]
                    )
                    data[f'current{i+1}'] = interpolated_current
                df = pd.DataFrame(data)
                output_file = 'current_circuit.csv'
                df.to_csv(output_file, index=False)
                print(f"Current data saved to {output_file}")
                
        except Exception as e:
            print(f"Error writing CSV file: {e}")

        # Change back to original directory
        if args.input_dir is not None:
            os.chdir(cwd)
            
        return 0
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())