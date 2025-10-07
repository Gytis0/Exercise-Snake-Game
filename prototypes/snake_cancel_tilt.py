from sense_hat import SenseHat
import math
import time
import random

# -------------------------------
# Setup
# -------------------------------
sense = SenseHat()
sense.low_light = True

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
NO_LED = (0, 0, 0)


def five_img():
    W = WHITE
    O = NO_LED
    img = [O, O, W, W, W, W, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, W, W, W, W, O, O,]
    return img


def four_img():
    W = WHITE
    O = NO_LED
    img = [O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, W, O, O, O,
        O, O, W, W, W, W, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,]
    return img


def three_img():
    W = WHITE
    O = NO_LED
    img = [O, O, W, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, W, W, W, W, O, O,]
    return img


def two_img():
    W = WHITE
    O = NO_LED
    img = [O, O, W, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, W, W, W, W, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, W, W, W, O, O,]
    return img


def one_img():
    W = WHITE
    O = NO_LED
    img = [O, O, O, O, W, O, O, O,
        O, O, O, W, W, O, O, O,
        O, O, W, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, W, W, W, O, O,]
    return img


images = [five_img, four_img, three_img, two_img, one_img]
COUNTDOWN_DELAY = 0.7
MATRIX_MIN_VALUE = 0
MATRIX_MAX_VALUE = 7
MATRIX_SIZE = 8

# -------------------------------
# Accelerometer / Movement
# -------------------------------
THRESHOLD = 0.25  # g
POLL_RATE = 0.01

cached_pitch = 0.0
cached_roll = 0.0
cached_x = 0.0
cached_y = 0.0
cached_z = 0.0
time_last = 0

def poll_readings():
    global cached_pitch, cached_roll, cached_x, cached_y, cached_z, time_last
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
    
    gravity_x = -math.sin(cached_pitch)
    gravity_y = math.sin(cached_roll)
    gravity_z = -math.cos(cached_pitch) * math.cos(cached_roll)
    
    ax_true = cached_x - gravity_x
    ay_true = cached_y - gravity_y
    az_true = cached_z - gravity_z
    
    return {'x': ax_true, 'y': ay_true, 'z': az_true}

def get_movement_tilt_corrected():
    poll_readings()
    acc = get_acceleration_without_tilt()
    
    if abs(acc['x']) > abs(acc['y']):
        if acc['x'] > THRESHOLD:
            return (1, 0)   # right
        elif acc['x'] < -THRESHOLD:
            return (-1, 0)  # left
    else:
        if acc['y'] > THRESHOLD:
            return (0, 1)   # down
        elif acc['y'] < -THRESHOLD:
            return (0, -1)  # up
    return None

# -------------------------------
# Game loop
# -------------------------------
try:
    # Countdown
    for img in images:
        sense.set_pixels(img())
        time.sleep(COUNTDOWN_DELAY)

    # Snake setup
    snakePosX = [3]
    snakePosY = [6]
    movementX = 0
    movementY = -1

    # Food setup
    while True:
        foodPosX = random.randint(0, 7)
        foodPosY = random.randint(0, 7)
        if foodPosX != snakePosX[0] or foodPosY != snakePosY[0]:
            break

    snakeMovementDelay = 0.5
    snakeMovementDelayDecrease = -0.02
    gameOverFlag = False
    growSnakeFlag = False

    while not gameOverFlag:
        # Check if snake eats food
        if foodPosX == snakePosX[0] and foodPosY == snakePosY[0]:
            growSnakeFlag = True
            while True:
                foodPosX = random.randint(0, 7)
                foodPosY = random.randint(0, 7)
                if (foodPosX, foodPosY) not in zip(snakePosX, snakePosY):
                    break
            snakeMovementDelay += snakeMovementDelayDecrease

        # Check if snake bites itself
        for i in range(1, len(snakePosX)):
            if snakePosX[i] == snakePosX[0] and snakePosY[i] == snakePosY[0]:
                gameOverFlag = True

        if gameOverFlag:
            break

        # Detect movement
        move = get_movement_tilt_corrected()
        if move:
            dx, dy = move
            if dx != -movementX or dy != -movementY:  # prevent reversing
                movementX, movementY = dx, dy

        # Grow snake
        if growSnakeFlag:
            growSnakeFlag = False
            snakePosX.append(0)
            snakePosY.append(0)

        # Move snake
        for i in range(len(snakePosX)-1, 0, -1):
            snakePosX[i] = snakePosX[i-1]
            snakePosY[i] = snakePosY[i-1]

        snakePosX[0] += movementX
        snakePosY[0] += movementY

        # Wrap around
        snakePosX[0] %= MATRIX_SIZE
        snakePosY[0] %= MATRIX_SIZE

        # Draw
        sense.clear()
        sense.set_pixel(foodPosX, foodPosY, RED)
        for x, y in zip(snakePosX, snakePosY):
            sense.set_pixel(x, y, GREEN)

        time.sleep(snakeMovementDelay)

except KeyboardInterrupt:
    sense.clear()
    print("\nGame stopped.")
