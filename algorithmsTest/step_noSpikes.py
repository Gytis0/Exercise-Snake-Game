from sense_hat import SenseHat
import time
from collections import deque
from statistics import median
from lateralMovementOrientationCounter import get_acceleration_without_tilt, poll_readings

sense = SenseHat()

# PARAMETERS
STEP_THRESHOLD = 0.1         # dx threshold to detect a step
MIN_STEP_INTERVAL = 0.3      # minimum seconds between steps
DIRECTION_BUFFER_SIZE = 5    # number of last averages to infer direction
NOISE_THRESHOLD = 0.02       # ignore very small X readings

# DATA BUFFERS
x_buffer = deque()           # stores (timestamp, x_value)
direction_buffer = deque(maxlen=DIRECTION_BUFFER_SIZE)
last_step_time = 0

def get_smoothed_x():
    now = time.time()
    acc = get_acceleration_without_tilt()

    # ignore very small X values
    if abs(acc['x']) >= NOISE_THRESHOLD:
        x_buffer.append((now, acc['x']))

    # Remove old entries beyond MIN_STEP_INTERVAL
    while x_buffer and (now - x_buffer[0][0]) > MIN_STEP_INTERVAL:
        x_buffer.popleft()

    if len(x_buffer) < 2:
        return acc['x']

    # Spike-resistant averaging using median absolute deviation (MAD)
    values = [v for _, v in x_buffer]
    med = median(values)
    mad = median([abs(v - med) for v in values]) or 1e-9
    filtered = [v for v in values if abs(v - med) < 2 * mad]

    return sum(filtered) / len(filtered)

def detect_step_with_direction():
    global last_step_time, x_buffer
    current_time = time.time()
    x = get_smoothed_x()

    # Update direction buffer
    direction_buffer.append(x)

    if len(x_buffer) < 2:
        return None  # not enough data to compute dx

    # compute dx (derivative-like change)
    previous_avg = sum(v for _, v in list(x_buffer)[:-1]) / (len(x_buffer) - 1)
    dx = x - previous_avg

    # Step detection
    if abs(dx) > STEP_THRESHOLD and (current_time - last_step_time > MIN_STEP_INTERVAL):
        last_step_time = current_time

        # Direction from last few averages
        avg_recent = sum(direction_buffer) / len(direction_buffer)
        direction = 'right' if avg_recent > 0 else 'left'

        # Clear x_buffer to avoid old readings affecting next step
        x_buffer.clear()

        return direction

    return None

# MAIN LOOP
print("Starting step detection. Press Ctrl+C to stop.")

count = 0

try:
    while True:
        poll_readings()
        step_dir = detect_step_with_direction()
        if step_dir:
            print(f"Step detected! Direction: {step_dir}")
            # Display step count or direction
            count = (count + 1) % 10
            if step_dir == 'right':
                sense.show_letter('R', text_colour=[0, 255, 0])
            else:
                sense.show_letter('L', text_colour=[255, 0, 0])
            time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
