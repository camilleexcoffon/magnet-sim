# Magnet-Sim Documentation

Welcome to the documentation for Magnet-Sim, a Python package for simulating magnetically coupled RL circuits with PID control.

## Overview

Magnet-Sim provides a comprehensive framework for simulating complex electrical circuits with magnetic coupling between multiple circuits. It implements the true physics equations for magnetically coupled systems and includes advanced control algorithms.

## Physics Model

The simulation is based on the fundamental equation for magnetically coupled RL circuits:

```
U_i = R_i(I_i) × I_i + Σ L(i,j) × dI_j/dt
```

Where:
- `U_i`: Applied voltage to circuit i
- `R_i(I_i)`: Current-dependent resistance of circuit i  
- `L(i,j)`: Inductance/mutual inductance matrix element
- `I_j`: Current in circuit j
- The sum is over all circuits j in the system

## Key Features

### Core Capabilities
- **Multi-circuit simulation**: Support for N magnetically coupled circuits
- **Current-dependent resistance**: Non-linear resistance modeling R(I)
- **Magnetic coupling**: Full inductance matrix with mutual inductances
- **Multiple control modes**: PID current control, direct voltage control, or free response

### Advanced Features
- **Adaptive PID control**: Parameters automatically adjust based on operating conditions
- **Physics validation**: Built-in verification of circuit equations
- **Data integration**: CSV-based input/output for experimental data comparison
- **Comprehensive visualization**: Rich plotting with error analysis
- **Performance metrics**: Tracking accuracy and settling time analysis

### Software Engineering
- **Modular design**: Clean separation of physics, control, and data handling
- **Type safety**: Full type hints for better code reliability
- **Comprehensive testing**: Unit tests with >90% coverage
- **Professional packaging**: Standard Python package structure
- **Command-line interface**: Easy-to-use CLI for batch processing

## Quick Links

- [Getting Started](quickstart.md): Installation and first simulation
- [API Reference](api.md): Complete function and class documentation
- [Examples](../examples/): Working code examples
- [GitHub Repository](https://github.com/your-username/magnet-sim): Source code

## Installation

```bash
# From PyPI (when available)
pip install magnet-sim

# From source
git clone https://github.com/your-username/magnet-sim.git
cd magnet-sim
pip install -e .
```

## Basic Usage

### Python API
```python
from magnet_sim import simulate_magnetically_coupled_rl

results = simulate_magnetically_coupled_rl(
    resistance_csvs=['resistance.csv'],
    inputs_csv='targets.csv', 
    inductance_csv='inductance.csv',
    n_circuits=1,
    t_span=(0, 100),
    control_mode='pid'
)
```

### Command Line
```bash
magnet-sim --mode pid --n-circuits 2 --t-end 100 --save
```

## Support

- **Documentation**: This site and inline docstrings
- **Issues**: [GitHub Issues](https://github.com/your-username/magnet-sim/issues) 
- **Discussions**: [GitHub Discussions](https://github.com/your-username/magnet-sim/discussions)

## Citation

If you use Magnet-Sim in your research, please cite:

```bibtex
@software{magnet_sim,
  title={Magnet-Sim: A Python Package for Magnetically Coupled RL Circuit Simulation},
  author={Magnet Simulation Team},
  year={2024},
  url={https://github.com/your-username/magnet-sim}
}
```