from sense_hat import SenseHat
import time
from collections import deque
from .filteredAcceleration import get_filtered_acceleration, poll_readings

sense = SenseHat()

# PARAMETERS FOR FURTHER NOISE FILTERING
SMOOTH_THRESHOLD = 0.065     # MAX value that is considered as noise (for example, when PI is on the table, but the sensor still generates values)
REQUIRED_READINGS = 7        # minimum non-zero readings in window to infer a step

# SLIDING WINDOW PARAMETERS
MAX_WINDOW_TIME = 0.7        # maximum duration of movement window for averaging
WEIGHT_RECENT = 1            # multiplies most recent reading roughly by this value

# STEP DETECTION (MIN_STEP_INTERVAL must be higher than SETTLE_TIME)
MIN_STEP_INTERVAL = 0.4      # How much time passes between steps (should be around 0.25 - 0.5)
SETTLE_TIME = 0.15           # How much time has to pass after the step, to consider that the player has stopped moving

from collections import deque

class StepState:
    def __init__(self):
        self.last_step_time = 0.0
        self.movement_window_x = deque()  # stores (timestamp, x_value)
        self.movement_window_y = deque()  # stores (timestamp, y_value)
        self.step_in_progress_axis = {
            "x": False,
            "y": False
        }

step_state = StepState()

# Helper function for axis detection
def _detect_axis_step(window, axis_name, now):
    if not step_state.step_in_progress_axis[axis_name] and any(abs(v) >= SMOOTH_THRESHOLD for t, v in window):
        step_state.step_in_progress_axis[axis_name] = True

    if step_state.step_in_progress_axis[axis_name]:
        # Step ends if last SETTLE_TIME readings are near zero
        settled = True
        for t, v in reversed(window):
            if now - t > SETTLE_TIME:
                break
            if abs(v) >= SMOOTH_THRESHOLD:
                settled = False
                break

        if settled:
            xs = [v for t, v in window if v != 0.0]
            if len(xs) >= REQUIRED_READINGS:
                weights = [1 + (i / len(xs)) * (WEIGHT_RECENT - 1) for i in range(len(xs))]
                avg = sum(v * w for v, w in zip(xs, weights)) / sum(weights)
                step_state.step_in_progress_axis[axis_name] = False
                window.clear()
                return avg
            
    return None
        
def get_input():
    """
    Detects steps in X and Y axes and returns the dominant direction.
    Returns: None, "Left", "Right", "Forwards", or "Backwards"
    """

    now = time.time()
    poll_readings()
    acc = get_filtered_acceleration()
    x, y = acc['x'], acc['y']

    # Treat tiny movements as zero
    x = 0.0 if abs(x) < SMOOTH_THRESHOLD else x
    y = 0.0 if abs(y) < SMOOTH_THRESHOLD else y

    # Add readings to movement windows
    step_state.movement_window_x.append((now, x))
    step_state.movement_window_y.append((now, y))

    # Remove old readings beyond MAX_WINDOW_TIME
    while step_state.movement_window_x and (now - step_state.movement_window_x[0][0]) > MAX_WINDOW_TIME:
        step_state.movement_window_x.popleft()
    while step_state.movement_window_y and (now - step_state.movement_window_y[0][0]) > MAX_WINDOW_TIME:
        step_state.movement_window_y.popleft()

    step_detected = None

    # Cooldown check: skip step detection if still in cooldown
    if (now - step_state.last_step_time) < MIN_STEP_INTERVAL:
        return None

    # Detect step for each axis
    avg_x = _detect_axis_step(step_state.movement_window_x, "x", now)
    avg_y = _detect_axis_step(step_state.movement_window_y, "y", now)

    # If both axes are None, no step detected
    if avg_x is None and avg_y is None:
        return None

    # TODO : Return both axes. In game logic we can decide which axis to use. For example:
    # we would use X axis if the snake is going up or down
    # we would use Y axis if the snake is going left or right
    
    # Determine dominant axis
    if avg_x is not None and (avg_y is None or abs(avg_x) >= abs(avg_y)):
        step_state.last_step_time = now
        return "right" if avg_x > 0 else "left"
    elif avg_y is not None:
        step_state.last_step_time = now
        return "backwards" if avg_y > 0 else "forwards"

    return None
