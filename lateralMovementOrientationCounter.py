from sense_hat import SenseHat
import math
import time

sense = SenseHat()

# CONST
THRESHOLD = 0.25
# It's best to keep the polling rates synchronized
POLL_RATE = 0.01

# Global variables
cached_pitch = 0.0
cached_roll = 0.0
cached_acc = None

cached_x = 0.0
cached_y = 0.0
cached_z = 0.0

time_last = 0

def poll_readings():
    global cached_pitch, cached_roll, cached_acc
    global cached_x, cached_y, cached_z
    global time_last
    current_time = time.time()
    if current_time - time_last >= POLL_RATE:
        orientation = sense.get_orientation_degrees()
        cached_pitch = math.radians(orientation['pitch'])
        cached_roll = math.radians(orientation['roll'])
        
        accel = sense.get_accelerometer_raw()
        cached_x = accel['x']
        cached_y = accel['y']
        cached_z = accel['z']
        
        time_last = current_time
    
def get_acceleration_without_tilt():
	global cached_pitch, cached_roll, cached_x, cached_y, cached_z
	
	gravity_x = -1 * math.sin(cached_pitch)
	gravity_y = 1 * math.sin(cached_roll)
	gravity_z = -1 * math.cos(cached_pitch) * math.cos(cached_roll)
    
	ax_true = cached_x - gravity_x
	ay_true = cached_y - gravity_y
	az_true = cached_z - gravity_z
    
	return {
	'x': ax_true,
	'y': ay_true,
	'z': az_true,
	'gx': gravity_x
    }

def detect_lateral_movement(threshold, acc):
    if abs(acc['x']) > threshold:
        direction = "RIGHT" if acc['x'] > 0 else "LEFT"
        return True, direction, acc['x']
    
    return False, None, acc['x']

# Main loop example

try:
    while True:
        poll_readings()
        acc = get_acceleration_without_tilt()
        is_moving, direction, accel_x = detect_lateral_movement(THRESHOLD, acc)
        
        # Display information
        
        print(f"Pitch: {cached_pitch:6.1f}° | Roll: {cached_roll:6.1f}°")
        print(f"Raw X: {cached_x:6.3f}g | GX: {acc['gx']:6.3f}g")
        print(f"True X: {acc['x']:6.3f}g", end="")
        
        if is_moving:
            print(f" -> MOVING {direction}!")
            sense.show_letter(">" if direction == "RIGHT" else "<", text_colour=[255, 0, 0])
        else:
            print(" (stationary)")
            sense.clear()
        
        print("-" * 50)
        time.sleep(0.001)
        
except KeyboardInterrupt:
    sense.clear()
    print("\nStopped.")
