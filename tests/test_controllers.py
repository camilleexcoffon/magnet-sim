"""
Tests for PID controllers.
"""

import pytest
import numpy as np
from magnet_sim.core.controllers import PIDController, get_pid_params


class TestPIDController:
    """Test cases for PID controller functionality."""
    
    def test_pid_controller_initialization(self):
        """Test PID controller initialization."""
        pid = PIDController(
            fixed_setpoint=10.0,
            output_limits=(-100, 100),
            name="TestPID"
        )
        
        assert pid.fixed_setpoint == 10.0
        assert pid.output_limits == (-100, 100)
        assert pid.name == "TestPID"
        assert pid.first_call == True
        assert pid.integral == 0.0
        assert pid.prev_error == 0.0
    
    def test_pid_setpoint_function(self):
        """Test PID controller with setpoint function."""
        def setpoint_func(t):
            return 5.0 * t
        
        pid = PIDController(setpoint_func=setpoint_func)
        
        assert pid.get_setpoint(0) == 0.0
        assert pid.get_setpoint(2) == 10.0
        assert pid.get_setpoint(5) == 25.0
    
    def test_pid_fixed_setpoint(self):
        """Test PID controller with fixed setpoint."""
        pid = PIDController(fixed_setpoint=15.0)
        
        assert pid.get_setpoint(0) == 15.0
        assert pid.get_setpoint(10) == 15.0
        assert pid.get_setpoint(100) == 15.0
    
    def test_pid_compute_basic(self):
        """Test basic PID computation."""
        pid = PIDController(fixed_setpoint=10.0)
        
        # First call
        output1, setpoint1 = pid.compute(0.0, 0.0)
        assert setpoint1 == 10.0
        assert output1 != 0.0  # Should have some output due to error
        
        # Second call
        output2, setpoint2 = pid.compute(5.0, 1.0)
        assert setpoint2 == 10.0
        assert output2 != output1  # Output should change
    
    def test_pid_output_limits(self):
        """Test PID output limiting."""
        pid = PIDController(
            fixed_setpoint=1000.0,  # Large setpoint to force saturation
            output_limits=(-10, 10)
        )
        
        output, _ = pid.compute(0.0, 0.0)
        assert -10 <= output <= 10
    
    def test_pid_reset(self):
        """Test PID controller reset functionality."""
        pid = PIDController(fixed_setpoint=10.0)
        
        # Run some computations
        pid.compute(0.0, 0.0)
        pid.compute(5.0, 1.0)
        
        # Check that state has changed
        assert pid.first_call == False
        assert pid.prev_error != 0.0
        assert pid.prev_time != 0.0
        
        # Reset
        pid.reset()
        
        # Check that state is reset
        assert pid.first_call == True
        assert pid.prev_error == 0.0
        assert pid.prev_time == 0.0
        assert pid.integral == 0.0


class TestPIDParams:
    """Test cases for adaptive PID parameters."""
    
    def test_get_pid_params_low_current(self):
        """Test PID parameters for low current."""
        Kp, Ki, Kd = get_pid_params(30.0, 10.0)
        assert Kp == 5
        assert Ki == 0.2
        assert Kd == 0
    
    def test_get_pid_params_medium_current(self):
        """Test PID parameters for medium current."""
        Kp, Ki, Kd = get_pid_params(200.0, 10.0)
        assert Kp == 12
        assert Ki == 1
        assert Kd == 0
    
    def test_get_pid_params_high_current(self):
        """Test PID parameters for high current."""
        Kp, Ki, Kd = get_pid_params(1000.0, 10.0)
        assert Kp == 12
        assert Ki == 1
        assert Kd == 0
    
    def test_get_pid_params_boundary_conditions(self):
        """Test PID parameters at boundary conditions."""
        # Exactly at boundary
        Kp, Ki, Kd = get_pid_params(60.0, 10.0)
        assert Kp == 5  # Should use low current params
        
        Kp, Ki, Kd = get_pid_params(800.0, 10.0)
        assert Kp == 12  # Should use medium current params