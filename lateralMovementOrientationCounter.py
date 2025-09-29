from sense_hat import SenseHat
import time

sense = SenseHat()

while True:
    acc = sense.get_accelerometer_raw()
    orientation = sense.get_orientation_degrees()
    
    x = acc['x']
    y = acc['y']
    z = acc['z']

    pitch = orientation['pitch']
    roll = orientation['roll']
    
    # Debug print
    print(f"Raw Accel: X={x:.3f}, Y={y:.3f}, Z={z:.3f}")
    print(f"Orientation: Pitch={pitch:.2f}, Roll={roll:.2f}")

    # You can now use pitch/roll to rotate the acceleration vector if needed

    time.sleep(0.1)