from sense_hat import SenseHat
import time
import random
import os
import sys

SNAKE_SPEED = float(os.getenv("SNAKE_SPEED", "0.15"))

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from sensorScripts import playerInput

senseHat = SenseHat()
senseHat.low_light = True

GREEN = (0, 255, 0)
RED   = (255, 0, 0)
WHITE = (255, 255, 255)
NO_LED = (0, 0, 0)

def five_img():
    W, O = WHITE, NO_LED
    return [O,O,W,W,W,W,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,W,W,W,W,O,O]

def four_img():
    W, O = WHITE, NO_LED
    return [O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,W,O,O,O,
            O,O,W,W,W,W,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O]

def three_img():
    W, O = WHITE, NO_LED
    return [O,O,W,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,W,W,W,W,O,O]

def two_img():
    W, O = WHITE, NO_LED
    return [O,O,W,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,W,W,W,W,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,W,W,W,O,O]

def one_img():
    W, O = WHITE, NO_LED
    return [O,O,O,O,W,O,O,O,
            O,O,O,W,W,O,O,O,
            O,O,W,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,W,W,W,O,O]

images = [five_img, four_img, three_img, two_img, one_img]

COUNTDOWN_DELAY = 0.70
MATRIX_MIN_VALUE = 0
MATRIX_MAX_VALUE = 7
MATRIX_SIZE = 8
COUNTDOWN_DELAY   = 0.70
MATRIX_MIN_VALUE  = 0
MATRIX_MAX_VALUE  = 7
MATRIX_SIZE       = 8
>>>>>>> debef56 (Update: HPF/STEP/CXLT modes; imports and menu speed; bugfixes)

while True:
    gameOverFlag = False
    growSnakeFlag = False
    generateRandomFoodFlag = False

    snakeMovementDelay = SNAKE_SPEED
    snakeMovementDelayDecrease = -0.02

    for img in images:
        senseHat.set_pixels(img())
        time.sleep(COUNTDOWN_DELAY)

    snakePosX = [3]
    snakePosY = [6]
    movementX, movementY = 0, -1

    while True:
        foodPosX = random.randint(0, 7)
        foodPosY = random.randint(0, 7)
        if foodPosX != snakePosX[0] or foodPosY != snakePosY[0]:
            break

    lastMoveTime = time.time()

    while not gameOverFlag:
        move = playerInput.get_input()
        dx, dy = movementX, movementY
        if move == "left":
            dx, dy = -1, 0
        elif move == "right":
            dx, dy = 1, 0
        elif move == "forwards":
            dx, dy = 0, -1
        elif move == "backwards":
            dx, dy = 0, 1

        if not (dx == -movementX and dy == -movementY):
            movementX, movementY = dx, dy

        now = time.time()
        if now - lastMoveTime >= snakeMovementDelay:
            lastMoveTime = now

            if foodPosX == snakePosX[0] and foodPosY == snakePosY[0]:
                growSnakeFlag = True
                generateRandomFoodFlag = True
                snakeMovementDelay = max(0.03, snakeMovementDelay + snakeMovementDelayDecrease)

            for i in range(1, len(snakePosX)):
                if snakePosX[i] == snakePosX[0] and snakePosY[i] == snakePosY[0]:
                    gameOverFlag = True
                    break
            if gameOverFlag:
                break

            if growSnakeFlag:
                growSnakeFlag = False
                snakePosX.append(0)
                snakePosY.append(0)

            for i in range(len(snakePosX) - 1, 0, -1):
                snakePosX[i] = snakePosX[i - 1]
                snakePosY[i] = snakePosY[i - 1]

            snakePosX[0] += movementX
            snakePosY[0] += movementY

            if snakePosX[0] > MATRIX_MAX_VALUE:
                snakePosX[0] -= MATRIX_SIZE
            elif snakePosX[0] < MATRIX_MIN_VALUE:
                snakePosX[0] += MATRIX_SIZE
            if snakePosY[0] > MATRIX_MAX_VALUE:
                snakePosY[0] -= MATRIX_SIZE
            elif snakePosY[0] < MATRIX_MIN_VALUE:
                snakePosY[0] += MATRIX_SIZE

            if generateRandomFoodFlag:
                generateRandomFoodFlag = False
                while True:
                    foodPosX = random.randint(0, 7)
                    foodPosY = random.randint(0, 7)
                    if all(not (x == foodPosX and y == foodPosY) for x, y in zip(snakePosX, snakePosY)):
                        break

            senseHat.clear()
            senseHat.set_pixel(foodPosX, foodPosY, RED)
            for x, y in zip(snakePosX, snakePosY):
                senseHat.set_pixel(x, y, GREEN)
