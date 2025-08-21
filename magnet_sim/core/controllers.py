"""
PID controllers for circuit simulation.
"""

from typing import Optional, Tuple, Callable


def get_pid_params(current: float, t: float) -> Tuple[float, float, float]:
    """
    Get adaptive PID parameters based on current and time.
    
    Parameters
    ----------
    current : float
        Current value in Amperes
    t : float
        Time in seconds
        
    Returns
    -------
    Tuple[float, float, float]
        (Kp, Ki, Kd) PID parameters
    """
    # Adjust parameters directly based on current intensity
    if current <= 60:
        return 5, 0.2, 0   # Kp, Ki, Kd for low current
    elif current <= 800: 
        return 12, 1, 0    # Kp, Ki, Kd for medium current
    else:
        return 12, 1, 0    # Kp, Ki, Kd for high current


class PIDController:
    """
    Enhanced PID Controller with adaptive parameters.
    
    This controller implements a PID control algorithm with optional
    adaptive parameter tuning based on process variable values.
    """
    
    def __init__(
        self,
        setpoint_func: Optional[Callable[[float], float]] = None,
        fixed_setpoint: Optional[float] = None,
        output_limits: Optional[Tuple[float, float]] = None,
        name: Optional[str] = None,
        t_start= None,
    ):
        """
        Initialize PID controller.
        
        Parameters
        ----------
        setpoint_func : Optional[Callable[[float], float]]
            Function that returns setpoint given time
        fixed_setpoint : Optional[float]
            Fixed setpoint value (used if setpoint_func is None)
        output_limits : Optional[Tuple[float, float]]
            (min, max) output limits
        name : Optional[str]
            Controller name for identification
        """
        self.Kp = 0.0
        self.Ki = 0.0
        self.Kd = 0.0
        self.setpoint_func = setpoint_func
        self.fixed_setpoint = fixed_setpoint
        self.output_limits = output_limits
        self.name = name if name else "PID"
        self.t_start = t_start

        # Initialize error terms
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = t_start
        self.first_call = True
        self.prev_Ki = 0.0


    def get_setpoint(self, t: float) -> float:
        """
        Get setpoint at given time.
        
        Parameters
        ----------
        t : float
            Time value
            
        Returns
        -------
        float
            Setpoint value
        """
        if self.setpoint_func is not None:
            return self.setpoint_func(t)
        return self.fixed_setpoint if self.fixed_setpoint is not None else 0.0

    def compute(self, process_variable: float, current_time: float) -> Tuple[float, float]:
        """
        Compute PID output.
        
        Parameters
        ----------
        process_variable : float
            Current process variable value
        current_time : float
            Current time
            
        Returns
        -------
        Tuple[float, float]
            (output, setpoint) tuple
        """
        setpoint = self.get_setpoint(current_time)
        error = setpoint - process_variable
        
        if self.first_call:
            dt = 0.001
            
        else:
            dt = current_time - self.prev_time
            dt = max(dt, 0.001)
        
        # Get adaptive PID parameters
        Kp, Ki, Kd = get_pid_params(process_variable, current_time)
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        
        # Proportional term
        proportional = self.Kp * error
        
        # Integral term with anti-windup
        if abs(Ki - self.prev_Ki) > 0.01:
            self.integral = self.integral * self.prev_Ki / Ki  # Progressive damping
        
        self.integral += error * dt
        integral_term = self.Ki * self.integral
        
        # Derivative term
        
        if self.first_call : 
            derivative_term = 0
            self.first_call = False
        else : 
            derivative = (error - self.prev_error) / dt if dt > 0 else 0
            derivative_term = self.Kd * derivative
        # Calculate output
        output = proportional + integral_term + derivative_term

        # Apply output limits
        if self.output_limits is not None:
            output = max(self.output_limits[0], min(output, self.output_limits[1]))

        # Update state variables
        self.prev_error = error
        self.prev_time = current_time
        self.prev_Ki = Ki

        return output, setpoint
    
    def reset(self) -> None:
        """Reset controller state."""
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = 0.0
        self.first_call = True
        self.prev_Ki = 0.0