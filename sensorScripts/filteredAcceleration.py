from sense_hat import SenseHat
import math
import time

sense = SenseHat()

# It's best to keep the polling rates synchronized
POLL_RATE = 0.001

# Global variables
cached_pitch = 0.0
cached_roll = 0.0

cached_x = 0.0
cached_y = 0.0
cached_z = 0.0

time_last = 0

# Polls readings from the accelerometer and the compass at the specified POLL_RATE
# Run this method as often as possible
def poll_readings():
    global cached_pitch, cached_roll, cached_x, cached_y, cached_z, time_last

    now = time.time()
    if now - time_last < POLL_RATE:
        return

    to_rad = math.radians

    orientation = sense.get_orientation_degrees()
    cached_pitch = to_rad(orientation.get('pitch', 0.0))
    cached_roll = to_rad(orientation.get('roll', 0.0))

    accel = sense.get_accelerometer_raw()
    cached_x = accel.get('x', 0.0)
    cached_y = accel.get('y', 0.0)
    cached_z = accel.get('z', 0.0)

    time_last = now

# Computes and returns true raw X without the tilt interference
def get_filtered_acceleration():
    global cached_pitch, cached_roll, cached_x, cached_y, cached_z

    gravity_x = -math.sin(cached_pitch)
    gravity_y = math.sin(cached_roll)
    gravity_z = -math.cos(cached_pitch) * math.cos(cached_roll)

    return {
        'x': cached_x - gravity_x,
        'y': cached_y - gravity_y,
        'z': cached_z - gravity_z
    }
