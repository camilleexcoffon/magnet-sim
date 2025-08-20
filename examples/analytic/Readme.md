# Analytical test case

the following examples demonstrate how to run magnet_sim using analytical reference values for one RL circuit. These tests allow users to verify that the simulated currents and voltages match the analytical solutions. Both 'voltage' and 'pid' control modes are illustrated.  

# Voltage Mode

```bash
python -m  magnet_sim.cli.main \
   --resistance-files resistance_circuit.csv \
   --inductance-file inductance_matrix.csv \
   --inputs-file inputs_circuits_voltages.csv \
   --expected-values expected_circuits_currents.csv \
   --t-end 60 --n-circuits 1
```

# PID mode

```bash
python -m  magnet_sim.cli.main  \
   --resistance-files examples/analytic/resistance_circuit.csv \
   --inductance-file examples/analytic/inductance_matrix.csv \
   --inputs-file examples/analytic/expected_circuits_currents.csv \
   --expected-values examples/analytic/inputs_circuits_voltages.csv \
   --t-end 60--n-circuits --mode 'pid'
```