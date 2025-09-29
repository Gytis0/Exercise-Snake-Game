from sense_hat import SenseHat
import time
import math

sense = SenseHat()
last_time = time.time()
roll = 0.0
pitch = 0.0
threshold = 0.3
step_cooldown = 0.3
last_step_time = 0

while True:
    now = time.time()
    dt = now - last_time
    last_time = now

    # Read sensors
    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()  # degrees/sec

    # Integrate gyro to get tilt angles (convert to radians)
    roll += math.radians(gyro['x']) * dt
    pitch += math.radians(gyro['y']) * dt

    # Gravity projection
    g = 1.0  # 1 g
    g_x = g * math.sin(roll)
    g_y = g * math.sin(pitch)

    # Linear acceleration (remove gravity)
    linear_x = accel['x'] - g_x

    # Step detection
    if now - last_step_time > step_cooldown:
        if linear_x > threshold:
            print("Step right detected")
            last_step_time = now
        elif linear_x < -threshold:
            print("Step left detected")
            last_step_time = now

    time.sleep(0.01)
