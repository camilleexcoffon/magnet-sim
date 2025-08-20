"""
Configuration and argument parsing utilities.
"""

import argparse
import os
from typing import Any


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments for circuit simulation."""
    parser = argparse.ArgumentParser(
        description="Circuit simulation with magnetic coupling and PID control",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Time span parameters
    parser.add_argument(
        '--t-start', 
        type=float, 
        default=0, 
        help='Start time for simulation'
    )
    parser.add_argument(
        '--t-end', 
        type=float, 
        default=130, 
        help='End time for simulation'
    )
    
    # Circuit configuration
    parser.add_argument(
        '--n-circuits', 
        type=int, 
        default=1, 
        help='Number of circuits in the system'
    )
    
    # File paths
    parser.add_argument(
        '--resistance-files', 
        nargs='+', 
        default=["resistance_circuit.csv"], 
        help='List of resistance CSV files (one per circuit)'
    )
    parser.add_argument(
        '--inductance-file', 
        type=str, 
        default="inductance_matrix.csv", 
        help='Inductance matrix CSV file'
    )
    parser.add_argument(
        '--inputs-file', 
        type=str, 
        default="inputs_circuits_voltages.csv", 
        help='Input voltages/targets CSV file'
    )

    # PID parameters (optional - can be empty by default)
    parser.add_argument(
        '--pid-params', 
        nargs='*', 
        default=[], 
        help='PID parameters (format: Kp,Ki,Kd for each circuit)'
    )
    
    # Additional parameters
    parser.add_argument(
        '--input-dir', 
        type=str, 
        default='.', 
        help='Directory for inputs'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='.', 
        help='Output directory for results'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Enable verbose output'
    )

    parser.add_argument(
        '--save',
        action='store_true',
        help='Save graph in ODE directory'
    )

    parser.add_argument(
        '--expected-values',
        type=str,
        default="expected_circuits_currents.csv", 
        help='Output current/targets CSV file' 
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['voltage', 'pid'],
        default="voltage",
        help="Control mode: voltage or pid"
    )
    
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> bool:
    """
    Validate parsed arguments.
    
    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments
        
    Returns
    -------
    bool
        True if validation passes
        
    Raises
    ------
    ValueError
        If validation fails
    FileNotFoundError
        If required files don't exist
    """
    # Check that number of resistance files matches number of circuits
    if len(args.resistance_files) != args.n_circuits:
        raise ValueError(
            f"Number of resistance files ({len(args.resistance_files)}) "
            f"must match number of circuits ({args.n_circuits})"
        )
    
    # Check file existence
    files_to_check = args.resistance_files + [args.inductance_file, args.inputs_file]
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
    
    # Validate PID parameters if provided
    if args.pid_params and len(args.pid_params) != args.n_circuits:
        raise ValueError(
            f"Number of PID parameter sets ({len(args.pid_params)}) "
            f"must match number of circuits ({args.n_circuits})"
        )
    
    return True