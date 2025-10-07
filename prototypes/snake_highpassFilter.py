from sense_hat import SenseHat
import time
import random
from lateralMovementOrientationCounter import get_acceleration_without_tilt, poll_readings

senseHat = SenseHat()
senseHat.low_light = True

GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
NO_LED = (0, 0, 0)

# CONST
THRESHOLD = 0.25


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

COUNTDOWN_DELAY = 0.70
MATRIX_MIN_VALUE = 0
MATRIX_MAX_VALUE = 7
MATRIX_SIZE = 8

senseHat.set_imu_config(False, False, False)

from sense_hat import SenseHat
import time, random

senseHat = SenseHat()
senseHat.low_light = True
senseHat.set_imu_config(True, False, False)  # enable accelerometer only

GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
NO_LED = (0, 0, 0)

# ==============================
# Movement detection setup
# ==============================
alpha = 0.8            # smoothing factor for high-pass filter
threshold = 2        # movement threshold (tune!)
step_cooldown = 0.5    # seconds between direction changes (better to keep it lower than the speed of the snake so input will not be missed)

last_x, last_y = 0, 0
last_filtered_x, last_filtered_y = 0, 0
last_step_time = time.time()

def get_movement():
    """
    Detect step-based movement from accelerometer.
    Returns a direction vector (dx, dy) or None if no new step detected.
    """
    global last_x, last_y, last_filtered_x, last_filtered_y, last_step_time

    accel = senseHat.get_accelerometer_raw()
    x = accel['x'] * 10
    y = accel['y'] * 10

    # High-pass filter
    x_filtered = alpha * (last_filtered_x + x - last_x)
    y_filtered = alpha * (last_filtered_y + y - last_y)

    last_x, last_y = x, y
    last_filtered_x, last_filtered_y = x_filtered, y_filtered

    current_time = time.time()
    if current_time - last_step_time > step_cooldown:
        if abs(x_filtered) > abs(y_filtered):
            if x_filtered > threshold:
                last_step_time = current_time
                return (1, 0)   # right
            elif x_filtered < -threshold:
                last_step_time = current_time
                return (-1, 0)  # left
        else:
            if y_filtered > threshold:
                last_step_time = current_time
                return (0, 1)   # down
            elif y_filtered < -threshold:
                last_step_time = current_time
                return (0, -1)  # up
    return None


while True:
    # variables:
    gameOverFlag = False
    growSnakeFlag = False
    generateRandomFoodFlag = False
    snakeMovementDelay = 0.5
    snakeMovementDelayDecrease = -0.02

    # start countdown:
    for img in images:
        senseHat.set_pixels(img())
        time.sleep(COUNTDOWN_DELAY)

    # set default snake starting position (values are just chosen by preference):
    snakePosX = [3]
    snakePosY = [6]

    # generate random food position:
    while True:
        foodPosX = random.randint(0, 7)
        foodPosY = random.randint(0, 7)
        if foodPosX != snakePosX[0] or foodPosY != snakePosY[0]:
            break

    # set default snake starting direction (values are just chosen by preference):
    movementX = 0
    movementY = -1

    # -----------------------------------
    #             game loop
    # -----------------------------------
    while not gameOverFlag:
        # check if snake eats food:
        if foodPosX == snakePosX[0] and foodPosY == snakePosY[0]:
            growSnakeFlag = True
            generateRandomFoodFlag = True
            snakeMovementDelay += snakeMovementDelayDecrease

        # check if snake bites itself:
        for i in range(1, len(snakePosX)):
            if snakePosX[i] == snakePosX[0] and snakePosY[i] == snakePosY[0]:
                gameOverFlag = True

        # check if game-over:
        if gameOverFlag:
            break

        # #print("Gyro: {0}".format(senseHat.gyro_raw))
        # print("Acce: {0}".format(senseHat.accel_raw))
        # # check joystick events:
        move = get_movement_tilt_corrected()
        
        if move:
            dx, dy = move
            # Prevent reversing into itself
            if dx != -movementX or dy != -movementY:
                movementX, movementY = dx, dy
       
        # print(movementY)
        # grow snake:
        if growSnakeFlag:
            growSnakeFlag = False
            snakePosX.append(0)
            snakePosY.append(0)

        # move snake:
        for i in range((len(snakePosX) - 1), 0, -1):
            snakePosX[i] = snakePosX[i - 1]
            snakePosY[i] = snakePosY[i - 1]

        snakePosX[0] += movementX
        snakePosY[0] += movementY

        # check game borders:
        if snakePosX[0] > MATRIX_MAX_VALUE:
            snakePosX[0] -= MATRIX_SIZE
        elif snakePosX[0] < MATRIX_MIN_VALUE:
            snakePosX[0] += MATRIX_SIZE
        if snakePosY[0] > MATRIX_MAX_VALUE:
            snakePosY[0] -= MATRIX_SIZE
        elif snakePosY[0] < MATRIX_MIN_VALUE:
            snakePosY[0] += MATRIX_SIZE

        # spawn random food:
        if generateRandomFoodFlag:
            generateRandomFoodFlag = False
            retryFlag = True
            while retryFlag:
                foodPosX = random.randint(0, 7)
                foodPosY = random.randint(0, 7)
                retryFlag = False
                for x, y in zip(snakePosX, snakePosY):
                    if x == foodPosX and y == foodPosY:
                        retryFlag = True
                        break

        # update matrix:
        senseHat.clear()
        senseHat.set_pixel(foodPosX, foodPosY, RED)
        for x, y in zip(snakePosX, snakePosY):
            senseHat.set_pixel(x, y, GREEN)

        # snake speed (game loop delay):
        time.sleep(snakeMovementDelay)
