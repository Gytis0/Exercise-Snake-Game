from sense_hat import SenseHat
import time
from collections import deque
from lateralMovementOrientationCounter import get_acceleration_without_tilt, poll_readings

sense = SenseHat()

# PARAMETERS
SPIKE_THRESHOLD = 0.2
SMOOTH_THRESHOLD = 0.05
MIN_STEP_INTERVAL = 0.5
SETTLE_TIME = 0.2
MAX_SEQUENCE_TIME = 1.0  # max seconds to store for step pattern

# STATE
class StepState:
    def __init__(self):
        self.sequence = deque()  # store (timestamp, x_value)
        self.last_step_time = 0
        self.last_spike_time = 0

step_state = StepState()

def detect_step_smooth():
    now = time.time()
    x = get_acceleration_without_tilt()['x']

    # ignore tiny noise
    if abs(x) < SMOOTH_THRESHOLD:
        x = 0.0
    
    print(f'x: {x}')
    # add reading to sequence
    step_state.sequence.append((now, x))

    # remove old readings
    while step_state.sequence and (now - step_state.sequence[0][0]) > MAX_SEQUENCE_TIME:
        step_state.sequence.popleft()

    step_detected = None

    # update last spike time
    if abs(x) > SPIKE_THRESHOLD:
        step_state.last_spike_time = now

    # check if movement has settled
    if abs(x) <= SMOOTH_THRESHOLD and (now - step_state.last_spike_time) > SETTLE_TIME:
        xs = [v for t, v in step_state.sequence]

        # If sequence contains spikes, use previous logic
        if any(v > SPIKE_THRESHOLD for v in xs) and any(v < -SPIKE_THRESHOLD for v in xs):
            first_sign = +1 if xs.index(max(xs)) < xs.index(min(xs)) else -1
            step_detected = 'left' if first_sign == +1 else 'right'
        # Otherwise, smooth movement: average sign determines direction
        else:
            avg = sum(xs) / len(xs)
            if abs(avg) >= SMOOTH_THRESHOLD:  # ignore tiny average noise
                step_detected = 'left' if avg > 0 else 'right'

        # enforce minimum interval
        if step_detected and (now - step_state.last_step_time) > MIN_STEP_INTERVAL:
            step_state.last_step_time = now
            step_state.sequence.clear()  # reset for next step

    return step_detected

# MAIN LOOP
print("Starting smooth-step detection. Press Ctrl+C to stop.")

count = 0
try:
    while True:
        poll_readings()
        step_dir = detect_step_smooth()
        if step_dir:
            print(f"Step detected! Direction: {step_dir}")
            count = (count + 1) % 10
            if step_dir == 'left':
                sense.show_letter('L', text_colour=[255, 0, 0])
            else:
                sense.show_letter('R', text_colour=[0, 255, 0])
            time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
