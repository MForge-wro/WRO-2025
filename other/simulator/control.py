import time

# Try to import RPi.GPIO, if not available, we're in simulation mode
try:
    import RPi.GPIO as GPIO
    SIMULATION_MODE = False
except ImportError:
    SIMULATION_MODE = True
    # print("Running in simulation mode - RPi.GPIO not available")

# Pin Definitions (BCM Mode) - Configure these for your actual robot
# Drive Motor (Connected to one side of L298N)
DRIVE_MOTOR_IN1 = 17  # Example pin
DRIVE_MOTOR_IN2 = 27  # Example pin
DRIVE_MOTOR_ENA = 22  # Example PWM pin for speed control

# Steering Motor (Connected to the other side of L298N or a separate L298N)
STEER_MOTOR_IN1 = 5   # Example pin
STEER_MOTOR_IN2 = 6   # Example pin
STEER_MOTOR_ENB = 13  # Example PWM pin for speed/intensity control (optional for steering)

# PWM Frequency
PWM_FREQ = 100 # Hz

# Steering Parameters
MAX_STEER_ANGLE_PHYSICAL = 30.0  # degrees, physical limit of the wheels
# For simplicity, we'll assume direct control for now.
# Later, we might need calibration or feedback for precise angle control.

drive_pwm = None
steer_pwm = None # May not be needed if steering is just on/off or fixed intensity

def setup_gpio():
    """Initializes GPIO pins for motor control."""
    global drive_pwm, steer_pwm
    
    if SIMULATION_MODE:
        # print("Simulation: GPIO setup skipped")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Drive Motor Pins
    GPIO.setup(DRIVE_MOTOR_IN1, GPIO.OUT)
    GPIO.setup(DRIVE_MOTOR_IN2, GPIO.OUT)
    GPIO.setup(DRIVE_MOTOR_ENA, GPIO.OUT)
    GPIO.output(DRIVE_MOTOR_IN1, GPIO.LOW)
    GPIO.output(DRIVE_MOTOR_IN2, GPIO.LOW)
    try:
        drive_pwm = GPIO.PWM(DRIVE_MOTOR_ENA, PWM_FREQ)
        drive_pwm.start(0) # Start with 0% duty cycle (stopped)
    except Exception as e:
        # print(f"Error initializing drive_pwm: {e}")
        drive_pwm = None


    # Steering Motor Pins
    GPIO.setup(STEER_MOTOR_IN1, GPIO.OUT)
    GPIO.setup(STEER_MOTOR_IN2, GPIO.OUT)
    GPIO.output(STEER_MOTOR_IN1, GPIO.LOW)
    GPIO.output(STEER_MOTOR_IN2, GPIO.LOW)
    
    # Optional: PWM for steering intensity if needed
    # GPIO.setup(STEER_MOTOR_ENB, GPIO.OUT)
    # try:
    #     steer_pwm = GPIO.PWM(STEER_MOTOR_ENB, PWM_FREQ)
    #     steer_pwm.start(0)
    # except Exception as e:
    #     print(f"Error initializing steer_pwm: {e}")
    #     steer_pwm = None
    print("GPIO setup complete.")

def move_forward(speed_percent):
    """
    Moves the robot forward.
    speed_percent: 0-100
    """
    if SIMULATION_MODE:
        # print(f"Simulation: Moving forward at {speed_percent}%")
        move_forward.last_speed = speed_percent  # Store the last speed
        return

    if not drive_pwm:
        # print("Drive PWM not initialized.")
        return
    GPIO.output(DRIVE_MOTOR_IN1, GPIO.HIGH)
    GPIO.output(DRIVE_MOTOR_IN2, GPIO.LOW)
    drive_pwm.ChangeDutyCycle(max(0, min(100, speed_percent)))
    # print(f"Moving forward at {speed_percent}%")

def move_backward(speed_percent):
    """
    Moves the robot backward.
    speed_percent: 0-100
    """
    if SIMULATION_MODE:
        # print(f"Simulation: Moving backward at {speed_percent}%")
        return

    if not drive_pwm:
        # print("Drive PWM not initialized.")
        return
    GPIO.output(DRIVE_MOTOR_IN1, GPIO.LOW)
    GPIO.output(DRIVE_MOTOR_IN2, GPIO.HIGH)
    drive_pwm.ChangeDutyCycle(max(0, min(100, speed_percent)))
    # print(f"Moving backward at {speed_percent}%")

def stop_drive_motor():
    """Stops the drive motor."""
    if SIMULATION_MODE:
        # print("Simulation: Drive motor stopped")
        return

    if not drive_pwm:
        # print("Drive PWM not initialized (already stopped or error).")
        # Still try to set IN pins to LOW in case PWM failed but pins are set
        GPIO.output(DRIVE_MOTOR_IN1, GPIO.LOW)
        GPIO.output(DRIVE_MOTOR_IN2, GPIO.LOW)
        return
    GPIO.output(DRIVE_MOTOR_IN1, GPIO.LOW)
    GPIO.output(DRIVE_MOTOR_IN2, GPIO.LOW)
    drive_pwm.ChangeDutyCycle(0)
    # print("Drive motor stopped.")

def steer_left(intensity_percent=100):
    """
    Turns the steering motor to the left.
    intensity_percent: 0-100 (how hard to turn, if PWM is used for steering)
                       For now, it's effectively on/off.
    """
    if SIMULATION_MODE:
        # print(f"Simulation: Steering left at {intensity_percent}%")
        steer_left.last_direction = 'left'
        return

    GPIO.output(STEER_MOTOR_IN1, GPIO.HIGH)
    GPIO.output(STEER_MOTOR_IN2, GPIO.LOW)
    # if steer_pwm:
    #     steer_pwm.ChangeDutyCycle(max(0, min(100, intensity_percent)))
    # print(f"Steering left at {intensity_percent}% intensity")

def steer_right(intensity_percent=100):
    """
    Turns the steering motor to the right.
    intensity_percent: 0-100
    """
    if SIMULATION_MODE:
        # print(f"Simulation: Steering right at {intensity_percent}%")
        steer_left.last_direction = 'right'
        return

    GPIO.output(STEER_MOTOR_IN1, GPIO.LOW)
    GPIO.output(STEER_MOTOR_IN2, GPIO.HIGH)
    # if steer_pwm:
    #     steer_pwm.ChangeDutyCycle(max(0, min(100, intensity_percent)))
    # print(f"Steering right at {intensity_percent}% intensity")

def center_steering(): # Or stop_steering_motor
    """Stops the steering motor, ideally returning it to center.
    For a simple DC motor without feedback, this just stops it.
    More advanced control would require sensors or stepper motor.
    """
    if SIMULATION_MODE:
        # print("Simulation: Steering centered")
        steer_left.last_direction = 'center'
        return

    GPIO.output(STEER_MOTOR_IN1, GPIO.LOW)
    GPIO.output(STEER_MOTOR_IN2, GPIO.LOW)
    # if steer_pwm:
    #     steer_pwm.ChangeDutyCycle(0)
    # print("Steering motor stopped (centered).")

def cleanup_gpio():
    """Cleans up GPIO resources."""
    if SIMULATION_MODE:
        # print("Simulation: GPIO cleanup skipped")
        return

    # print("Cleaning up GPIO...")
    if drive_pwm:
        drive_pwm.stop()
    # if steer_pwm:
    #     steer_pwm.stop()
    GPIO.cleanup()
    # print("GPIO cleanup complete.")

# For simulation mode, we'll add a method to get the current motor states
def get_motor_states():
    """Returns the current motor states for simulation."""
    if not SIMULATION_MODE:
        return None
    
    # In simulation mode, we'll return the last commanded states
    # This can be used by the simulation to update the robot's position
    return {
        'drive_speed': getattr(move_forward, 'last_speed', 0),
        'steering_direction': getattr(steer_left, 'last_direction', 'center')
    }

# Example usage (for testing this file directly)
if __name__ == '__main__':
    try:
        setup_gpio()

        print("Testing Drive Motor...")
        move_forward(50)
        time.sleep(2)
        move_backward(30)
        time.sleep(2)
        stop_drive_motor()
        time.sleep(1)

        print("Testing Steering Motor...")
        steer_left()
        time.sleep(1) # Duration of steer depends on motor speed and desired angle
        center_steering() # Stop steering motor
        time.sleep(0.5)
        
        steer_right()
        time.sleep(1)
        center_steering()
        time.sleep(1)

    except KeyboardInterrupt:
        print("Test interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cleanup_gpio() 