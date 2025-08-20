# Analytical test case

bdkbmlk

# Voltage Mode

```bash
python -m  magnet_sim.cli.main \
   --n-circuits 1 \
   --resistance-files resistance_circuit.csv --inductance-file inductance_matrix.csv --expected-values expected_circuits_currents.csv --t-end 60 --inputs-file inputs_circuits_voltages.csv
```

# PID mode

```bash
python -m  magnet_sim.cli.main  \
   --n-circuits 1 \
   --resistance-files examples/analytic/resistance_circuit.csv \
   --inductance-file examples/analytic/inductance_matrix.csv \
   --inputs-file examples/analytic/expected_circuits_currents.csv \
   --t-end 60 \
   --expected-values examples/analytic/inputs_circuits_voltages.csv \
   --mode 'pid'
```