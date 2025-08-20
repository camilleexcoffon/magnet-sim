# Magnet-Sim

A Python package for simulating magnetically coupled RL circuits with PID control.

## Overview

Magnet-Sim provides a comprehensive framework for simulating complex electrical circuits with magnetic coupling between multiple circuits. The package includes:

- **Physics-based simulation**: True implementation of magnetically coupled RL circuit equations
- **PID control**: Advanced PID controllers with adaptive parameters
- **Data handling**: CSV-based input/output for easy integration with experimental data
- **Visualization**: Rich plotting capabilities for analysis and validation
- **Command-line interface**: Easy-to-use CLI for running simulations

## Features

### Core Physics
The simulation implements the true physics equation for magnetically coupled circuits:

```
U_i = R_i(I_i) * I_i + Σ L(i,j) * dI_j/dt
```

Where:
- `U_i`: Applied voltage to circuit i
- `R_i(I_i)`: Current-dependent resistance of circuit i
- `L(i,j)`: Inductance/mutual inductance matrix
- `I_j`: Current in circuit j

### Control Modes
- **Voltage mode**: Direct voltage specification
- **PID mode**: Current control with adaptive PID parameters
- **Free response**: Natural circuit behavior with no applied voltage

### Advanced Features
- Current-dependent resistance modeling
- Symmetric inductance matrix validation
- Coupling coefficient analysis
- Performance metrics and error analysis
- Experimental data comparison

## Installation

### From PyPI (when published)
```bash
pip install magnet-sim
```

### From source
```bash
git clone https://github.com/your-username/magnet-sim.git
cd magnet-sim
pip install -e .
```

### Development installation

```bash
git clone https://github.com/your-username/magnet-sim.git
cd magnet-sim
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If you wish to install the package, replace the last line above by:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Basic simulation with default parameters
magnet-sim

# Custom simulation with specific files
magnet-sim --n-circuits 2 \
          --resistance-files circuit1_resistance.csv circuit2_resistance.csv \
          --inductance-file inductance_matrix.csv \
          --inputs-file target_currents.csv \
          --mode pid \
          --t-end 100

# Voltage mode simulation
magnet-sim --mode voltage \
          --inputs-file applied_voltages.csv \
          --save
```

### Python API Usage

```python
from magnet_sim import simulate_magnetically_coupled_rl
from magnet_sim.utils import plot_results

# Run simulation
results = simulate_magnetically_coupled_rl(
    resistance_csvs=["resistance.csv"],
    inputs_csv="targets.csv",
    inductance_csv="inductance.csv",
    n_circuits=1,
    t_span=(0, 100),
    control_mode="pid"
)

# Plot results
plot_results(results)
```

## Input File Formats

### Resistance Files
CSV format with current and resistance columns:
```csv
current,resistance
0,1.0
10,1.2
20,1.5
...
```

### Inductance Matrix
NxN matrix without headers:
```csv
0.001,0.0002
0.0002,0.001
```

### Input Files
Time-series data for targets (PID mode) or voltages:
```csv
time,current1,current2
0,0,0
1,10,5
2,20,10
...
```

## Examples

The `examples/` directory contains complete simulation examples:

- `basic_simulation.py`: Single circuit PID control
- `multi_circuit.py`: Multiple coupled circuits
- `voltage_mode.py`: Direct voltage control
- `data/`: Sample input files

## API Reference

### Core Functions

#### `simulate_magnetically_coupled_rl()`
Main simulation function for magnetically coupled RL circuits.

**Parameters:**
- `resistance_csvs`: List of resistance CSV files
- `inputs_csv`: Input voltages/targets CSV file
- `inductance_csv`: Inductance matrix CSV file
- `n_circuits`: Number of circuits
- `t_span`: Time span tuple (start, end)
- `control_mode`: 'pid', 'voltage', or 'none'
- `initial_currents`: Initial current values

**Returns:**
Dictionary containing simulation results including times, currents, voltages, and analysis data.

### Utility Functions

#### `load_inductance_matrix()`
Load and validate inductance matrix from CSV.

#### `load_resistance_data()`
Load current-dependent resistance data.

#### `PIDController`
Advanced PID controller class with adaptive parameters.

## Testing

Run the test suite:
```bash
pytest
```

With coverage:
```bash
pytest --cov=magnet_sim
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/your-username/magnet-sim.git
cd magnet-sim
pip install -e ".[dev]"
pre-commit install  # If using pre-commit hooks
```

### Code Style

This project uses:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

Run all checks:
```bash
black magnet_sim/
flake8 magnet_sim/
mypy magnet_sim/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{magnet_sim,
  title={Magnet-Sim: A Python Package for Magnetically Coupled RL Circuit Simulation},
  author={Magnet Simulation Team},
  year={2024},
  url={https://github.com/your-username/magnet-sim}
}
```

## Changelog

### v0.1.0 (2024-08-19)
- Initial release
- Basic magnetically coupled RL circuit simulation
- PID control implementation
- Command-line interface
- CSV data handling
- Plotting and visualization

## Support

- Documentation: [Read the Docs](https://magnet-sim.readthedocs.io/)
- Issues: [GitHub Issues](https://github.com/your-username/magnet-sim/issues)
- Discussions: [GitHub Discussions](https://github.com/your-username/magnet-sim/discussions)