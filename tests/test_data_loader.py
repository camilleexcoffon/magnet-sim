"""
Tests for data loading utilities.
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import os
from magnet_sim.utils.data_loader import (
    load_inductance_matrix,
    load_resistance_data,
    load_electrical_inputs,
    load_electrical_outputs,
)


class TestDataLoader:
    """Test cases for data loading functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_inductance_matrix_valid(self):
        """Test loading valid inductance matrix."""
        # Create test inductance matrix
        L_matrix = np.array([[0.001, 0.0001], [0.0001, 0.002]])
        inductance_file = os.path.join(self.temp_dir, 'inductance.csv')
        pd.DataFrame(L_matrix).to_csv(inductance_file, header=False, index=False)
        
        loaded_matrix = load_inductance_matrix(inductance_file, 2)
        
        assert loaded_matrix.shape == (2, 2)
        np.testing.assert_array_almost_equal(loaded_matrix, L_matrix)
    
    def test_load_inductance_matrix_enforce_symmetry(self):
        """Test symmetry enforcement for inductance matrix."""
        # Create slightly asymmetric matrix
        L_matrix = np.array([[0.001, 0.0001], [0.00011, 0.002]])
        inductance_file = os.path.join(self.temp_dir, 'inductance.csv')
        pd.DataFrame(L_matrix).to_csv(inductance_file, header=False, index=False)
        
        loaded_matrix = load_inductance_matrix(inductance_file, 2)
        
        # Should be symmetric
        np.testing.assert_array_almost_equal(loaded_matrix, loaded_matrix.T)
    
    def test_load_inductance_matrix_wrong_size(self):
        """Test error handling for wrong matrix size."""
        # Create 3x3 matrix but expect 2x2
        L_matrix = np.eye(3) * 0.001
        inductance_file = os.path.join(self.temp_dir, 'inductance.csv')
        pd.DataFrame(L_matrix).to_csv(inductance_file, header=False, index=False)
        
        with pytest.raises(ValueError, match="Inductance matrix must be 2x2"):
            load_inductance_matrix(inductance_file, 2)
    
    def test_load_resistance_data_single_file(self):
        """Test loading resistance data from single file."""
        # Create test resistance data
        current = np.linspace(0, 100, 50)
        resistance = 0.001 + 0.0001 * current
        resistance_df = pd.DataFrame({
            'current': current,
            'resistance': resistance
        })
        resistance_file = os.path.join(self.temp_dir, 'resistance.csv')
        resistance_df.to_csv(resistance_file, index=False)
        
        R_funcs = load_resistance_data([resistance_file])
        
        assert len(R_funcs) == 1
        
        # Test interpolation
        test_current = 50.0
        expected_resistance = 0.001 + 0.0001 * test_current
        actual_resistance = R_funcs[0](test_current)
        assert abs(actual_resistance - expected_resistance) < 1e-6
    
    def test_load_resistance_data_multiple_files(self):
        """Test loading resistance data from multiple files."""
        # Create two different resistance files
        for i, multiplier in enumerate([1.0, 2.0]):
            current = np.linspace(0, 100, 50)
            resistance = (0.001 + 0.0001 * current) * multiplier
            resistance_df = pd.DataFrame({
                'current': current,
                'resistance': resistance
            })
            resistance_file = os.path.join(self.temp_dir, f'resistance_{i}.csv')
            resistance_df.to_csv(resistance_file, index=False)
        
        files = [
            os.path.join(self.temp_dir, 'resistance_0.csv'),
            os.path.join(self.temp_dir, 'resistance_1.csv')
        ]
        R_funcs = load_resistance_data(files)
        
        assert len(R_funcs) == 2
        
        # Test that functions are different
        test_current = 50.0
        r1 = R_funcs[0](test_current)
        r2 = R_funcs[1](test_current)
        assert abs(r2 - 2 * r1) < 1e-6
    
    def test_load_resistance_data_missing_columns(self):
        """Test error handling for missing columns in resistance file."""
        # Create file with wrong column names
        df = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [4, 5, 6]
        })
        resistance_file = os.path.join(self.temp_dir, 'bad_resistance.csv')
        df.to_csv(resistance_file, index=False)
        
        with pytest.raises(ValueError, match="must have 'current' and 'resistance' columns"):
            load_resistance_data([resistance_file])
    
    def test_load_electrical_inputs_pid_mode(self):
        """Test loading electrical inputs for PID mode."""
        # Create test input data
        time = np.linspace(0, 10, 100)
        input_df = pd.DataFrame({
            'time': time,
            'current1': np.sin(time),
            'current2': np.cos(time)
        })
        inputs_file = os.path.join(self.temp_dir, 'inputs.csv')
        input_df.to_csv(inputs_file, index=False)
        
        input_funcs, times, input_values = load_electrical_inputs(
            inputs_file, 2, input_type='pid'
        )
        
        assert len(input_funcs) == 2
        assert len(input_values) == 2
        # np.testing.assert_array_equal(times, time)
        np.testing.assert_array_almost_equal(times, time, decimal=10)
        
        # Test interpolation
        test_time = 5.0
        expected1 = np.sin(test_time)
        expected2 = np.cos(test_time)
        actual1 = input_funcs[0](test_time)
        actual2 = input_funcs[1](test_time)
        
        assert abs(actual1 - expected1) < 1e-2
        assert abs(actual2 - expected2) < 1e-2
    
    def test_load_electrical_inputs_voltage_mode(self):
        """Test loading electrical inputs for voltage mode."""
        # Create test voltage data
        time = np.linspace(0, 10, 100)
        input_df = pd.DataFrame({
            'time': time,
            'voltage1': np.ones_like(time) * 5.0,
            'voltage2': np.ones_like(time) * 3.0
        })
        inputs_file = os.path.join(self.temp_dir, 'voltages.csv')
        input_df.to_csv(inputs_file, index=False)
        
        input_funcs, times, input_values = load_electrical_inputs(
            inputs_file, 2, input_type='voltage'
        )
        
        assert len(input_funcs) == 2
        assert len(input_values) == 2
        
        # Test values
        assert abs(input_funcs[0](5.0) - 5.0) < 1e-6
        assert abs(input_funcs[1](5.0) - 3.0) < 1e-6
    
    def test_load_electrical_inputs_missing_time_column(self):
        """Test error handling for missing time column."""
        df = pd.DataFrame({
            'current1': [1, 2, 3],
            'current2': [4, 5, 6]
        })
        inputs_file = os.path.join(self.temp_dir, 'bad_inputs.csv')
        df.to_csv(inputs_file, index=False)
        
        with pytest.raises(ValueError, match="Required column 'time' not found"):
            load_electrical_inputs(inputs_file, 2, input_type='pid')
    
    def test_load_electrical_inputs_missing_input_columns(self):
        """Test error handling for missing input columns."""
        df = pd.DataFrame({
            'time': [0, 1, 2],
            'current1': [1, 2, 3]
            # Missing current2
        })
        inputs_file = os.path.join(self.temp_dir, 'incomplete_inputs.csv')
        df.to_csv(inputs_file, index=False)
        
        with pytest.raises(ValueError, match="Missing pid columns"):
            load_electrical_inputs(inputs_file, 2, input_type='pid')
    
    def test_load_electrical_outputs(self):
        """Test loading electrical outputs."""
        # Create test output data
        time = np.linspace(0, 10, 100)
        output_df = pd.DataFrame({
            'time': time,
            'voltage1': np.ones_like(time) * 2.0,
            'voltage2': np.ones_like(time) * 1.5
        })
        outputs_file = os.path.join(self.temp_dir, 'outputs.csv')
        output_df.to_csv(outputs_file, index=False)
        
        times, output_values = load_electrical_outputs(
            outputs_file, 2, output_type='target'
        )
        
        assert len(output_values) == 2
        # np.testing.assert_array_equal(times, time)
        np.testing.assert_array_almost_equal(times, time, decimal=10)
        np.testing.assert_array_almost_equal(output_values[0], 2.0)
        np.testing.assert_array_almost_equal(output_values[1], 1.5)
