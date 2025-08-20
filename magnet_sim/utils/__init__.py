"""
Utility modules for magnet-sim.
"""

from .data_loader import (
    load_inductance_matrix,
    load_resistance_data,
    load_electrical_inputs,
    load_electrical_outputs,
)
from .plotting import plot_magnetically_coupled_results
from .config import parse_arguments, validate_arguments

__all__ = [
    "load_inductance_matrix",
    "load_resistance_data", 
    "load_electrical_inputs",
    "load_electrical_outputs",
    "plot_magnetically_coupled_results",
    "parse_arguments",
    "validate_arguments",
]