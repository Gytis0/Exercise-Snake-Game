import time
import random
from display import Display

# Set this to false if you want to use Pi sensors instead
shouldEmulate = True

if shouldEmulate:
    from emulators.player_input_emulated import PlayerInputEmulated
    from emulators.sense_hat_emulated import SenseHatEmulated
    senseHat = SenseHatEmulated()
    playerInput = PlayerInputEmulated()
else:
    from sense_hat import SenseHat
    from sensorScripts.player_input import PlayerInput
    senseHat = SenseHat()
    playerInput = PlayerInput()


display = Display(senseHat)

MATRIX_MIN_VALUE = 0
MATRIX_MAX_VALUE = 7
MATRIX_SIZE = 8

# This gets more and more inefficient the longer the snake is
# If we run into performance issues on Pi, we can refactor this
def spawnFood(snakePosX, snakePosY):
    while True:
        x = random.randint(MATRIX_MIN_VALUE, MATRIX_MAX_VALUE)
        y = random.randint(MATRIX_MIN_VALUE, MATRIX_MAX_VALUE)
        if all(x != sx or y != sy for sx, sy in zip(snakePosX, snakePosY)):
            return x, y

while True:
    gameOverFlag = False
    growSnakeFlag = False
    snakeMovementDelay = 0.5
    snakeMovementDelayDecrease = -0.001

    snakePosX = [random.randint(MATRIX_MIN_VALUE, MATRIX_MAX_VALUE)]
    snakePosY = [random.randint(MATRIX_MIN_VALUE, MATRIX_MAX_VALUE)]

    foodPosX, foodPosY = spawnFood(snakePosX, snakePosY)
    display.draw_food(foodPosX, foodPosY)
    display.update_snake(snakePosX, snakePosY)
    
    background = display.get_current_frame(snakePosX, snakePosY, foodPosX, foodPosY)
    display.showCountdown(background)

    movementX = 0
    movementY = -1

    while not gameOverFlag:
        # Poll input as fast as possible
        move = playerInput.get_input()
        dx, dy = movementX, movementY
        if move:
            if move == "left":
                dx, dy = -1, 0
            elif move == "right":
                dx, dy = 1, 0
            elif move == "forwards":
                dx, dy = 0, -1
            elif move == "backwards":
                dx, dy = 0, 1
                
        # Prevent reversing into itself
        if dx != -movementX or dy != -movementY:
            movementX, movementY = dx, dy
                
        # Check if the snake is biting on itself
        for i in range(1, len(snakePosX)):
            if snakePosX[i] == snakePosX[0] and snakePosY[i] == snakePosY[0]:
                gameOverFlag = True

        if gameOverFlag:
            break

        if growSnakeFlag:
            growSnakeFlag = False
            snakePosX.append(0)
            snakePosY.append(0)
        
        snakeSize = len(snakePosX)

        for i in range(snakeSize - 1, 0, -1):
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

        # If the food is reached, eat it
        if foodPosX == snakePosX[0] and foodPosY == snakePosY[0]:
            growSnakeFlag = True
            snakeMovementDelay += snakeMovementDelayDecrease
            foodPosX, foodPosY = spawnFood(snakePosX, snakePosY)
            
        display.clear()
        display.draw_food(foodPosX, foodPosY)
        display.update_snake(snakePosX, snakePosY)

        time.sleep(snakeMovementDelay)
