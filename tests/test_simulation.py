"""
Tests for simulation functionality.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import os
from magnet_sim.core.simulation import simulate_magnetically_coupled_rl
from magnet_sim.utils.data_loader import load_inductance_matrix, load_resistance_data


class TestSimulation:
    """Test cases for simulation functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test resistance data
        current = np.linspace(0, 100, 50)
        resistance = 0.001 + 0.0001 * current
        resistance_df = pd.DataFrame({
            'current': current,
            'resistance': resistance
        })
        self.resistance_file = os.path.join(self.temp_dir, 'resistance.csv')
        resistance_df.to_csv(self.resistance_file, index=False)
        
        # Create test inductance matrix
        inductance_matrix = np.array([[0.001, 0.0001], [0.0001, 0.001]])
        self.inductance_file = os.path.join(self.temp_dir, 'inductance.csv')
        pd.DataFrame(inductance_matrix).to_csv(self.inductance_file, header=False, index=False)
        
        # Create test input data
        time = np.linspace(0, 10, 100)
        input_df = pd.DataFrame({
            'time': time,
            'current1': np.ones_like(time) * 10,
            'current2': np.ones_like(time) * 5
        })
        self.inputs_file = os.path.join(self.temp_dir, 'inputs.csv')
        input_df.to_csv(self.inputs_file, index=False)
    
    def test_load_inductance_matrix(self):
        """Test inductance matrix loading."""
        L_matrix = load_inductance_matrix(self.inductance_file, 2)
        
        assert L_matrix.shape == (2, 2)
        assert L_matrix[0, 0] == 0.001
        assert L_matrix[1, 1] == 0.001
        assert L_matrix[0, 1] == 0.0001
        assert L_matrix[1, 0] == 0.0001
    
    def test_load_resistance_data(self):
        """Test resistance data loading."""
        R_funcs = load_resistance_data([self.resistance_file])
        
        assert len(R_funcs) == 1
        
        # Test interpolation
        test_current = 50.0
        resistance = R_funcs[0](test_current)
        expected = 0.001 + 0.0001 * test_current
        assert abs(resistance - expected) < 1e-6
    
    def test_single_circuit_simulation(self):
        """Test single circuit simulation."""
        # Create single circuit data
        inductance_matrix = np.array([[0.001]])
        single_inductance_file = os.path.join(self.temp_dir, 'single_inductance.csv')
        pd.DataFrame(inductance_matrix).to_csv(single_inductance_file, header=False, index=False)
        
        time = np.linspace(0, 5, 50)
        input_df = pd.DataFrame({
            'time': time,
            'current1': np.ones_like(time) * 10
        })
        single_inputs_file = os.path.join(self.temp_dir, 'single_inputs.csv')
        input_df.to_csv(single_inputs_file, index=False)
        
        results = simulate_magnetically_coupled_rl(
            resistance_csvs=[self.resistance_file],
            inputs_csv=single_inputs_file,
            inductance_csv=single_inductance_file,
            n_circuits=1,
            t_span=(0, 5),
            initial_currents=[0.0],
            control_mode='pid'
        )
        
        assert 'times' in results
        assert 'individual_currents' in results
        assert 'voltages' in results
        assert len(results['individual_currents']) == 1
        assert len(results['voltages']) == 1
        assert results['n_circuits'] == 1
    
    def test_two_circuit_simulation(self):
        """Test two circuit simulation."""
        results = simulate_magnetically_coupled_rl(
            resistance_csvs=[self.resistance_file, self.resistance_file],
            inputs_csv=self.inputs_file,
            inductance_csv=self.inductance_file,
            n_circuits=2,
            t_span=(0, 5),
            initial_currents=[0.0, 0.0],
            control_mode='pid'
        )
        
        assert 'times' in results
        assert 'individual_currents' in results
        assert 'voltages' in results
        assert len(results['individual_currents']) == 2
        assert len(results['voltages']) == 2
        assert results['n_circuits'] == 2
        assert results['L_matrix'].shape == (2, 2)
    
    def test_voltage_mode_simulation(self):
        """Test voltage mode simulation."""
        # Create voltage input data
        time = np.linspace(0, 5, 50)
        voltage_df = pd.DataFrame({
            'time': time,
            'voltage1': np.ones_like(time) * 1.0,
            'voltage2': np.ones_like(time) * 0.5
        })
        voltage_file = os.path.join(self.temp_dir, 'voltages.csv')
        voltage_df.to_csv(voltage_file, index=False)
        
        results = simulate_magnetically_coupled_rl(
            resistance_csvs=[self.resistance_file, self.resistance_file],
            inputs_csv=voltage_file,
            inductance_csv=self.inductance_file,
            n_circuits=2,
            t_span=(0, 5),
            initial_currents=[0.0, 0.0],
            control_mode='voltage'
        )
        
        assert results['control_mode'] == 'voltage'
        assert len(results['individual_currents']) == 2
        assert len(results['voltages']) == 2
    
    def test_invalid_inputs(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            # Wrong number of circuits
            simulate_magnetically_coupled_rl(
                resistance_csvs=[self.resistance_file],
                inputs_csv=self.inputs_file,
                inductance_csv=self.inductance_file,
                n_circuits=3,  # Mismatch
                t_span=(0, 5),
                control_mode='pid'
            )
        
        with pytest.raises(ValueError):
            # Invalid control mode
            simulate_magnetically_coupled_rl(
                resistance_csvs=[self.resistance_file],
                inputs_csv=self.inputs_file,
                inductance_csv=self.inductance_file,
                n_circuits=1,
                t_span=(0, 5),
                control_mode='invalid'
            )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)