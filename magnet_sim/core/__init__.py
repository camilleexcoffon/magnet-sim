"""
Core simulation modules for magnet-sim.
"""

from .simulation import simulate_magnetically_coupled_rl
from .controllers import PIDController, get_pid_params
from .physics import magnetically_coupled_rl_system

__all__ = [
    "simulate_magnetically_coupled_rl",
    "PIDController", 
    "get_pid_params",
    "magnetically_coupled_rl_system",
]