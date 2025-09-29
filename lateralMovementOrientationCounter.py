from sense_hat import SenseHat
import time
import math

sense = SenseHat()

def adjust_for_tilt(acc, pitch, roll):
    """
    Rotate accelerometer vector by -pitch and -roll to cancel tilt.
    Returns the adjusted X (lateral acceleration).
    """
    # Convert angles to radians
    pitch_rad = math.radians(pitch)
    roll_rad = math.radians(roll)

    x, y, z = acc['x'], acc['y'], acc['z']

    # --- Step 1: undo pitch rotation around X-axis ---
    y2 = y * math.cos(-pitch_rad) - z * math.sin(-pitch_rad)
    z2 = y * math.sin(-pitch_rad) + z * math.cos(-pitch_rad)
    x2 = x  # unchanged by pitch rotation

    # --- Step 2: undo roll rotation around Y-axis ---
    x3 = x2 * math.cos(-roll_rad) + z2 * math.sin(-roll_rad)
    z3 = -x2 * math.sin(-roll_rad) + z2 * math.cos(-roll_rad)
    y3 = y2  # unchanged by roll rotation

    return x3, y3, z3  # adjusted accelerations in world frame

while True:
    acc = sense.get_accelerometer_raw()
    orientation = sense.get_orientation_degrees()

    pitch = orientation['pitch']
    roll = orientation['roll']

    adj_x, adj_y, adj_z = adjust_for_tilt(acc, pitch, roll)

    print(f"Raw Accel:  X={acc['x']:.3f}, Y={acc['y']:.3f}, Z={acc['z']:.3f}")
    print(f"Orientation: Pitch={pitch:.2f}, Roll={roll:.2f}")
    print(f"Adjusted:   X={adj_x:.3f}, Y={adj_y:.3f}, Z={adj_z:.3f}")
    print("-" * 40)

    time.sleep(0.1)
