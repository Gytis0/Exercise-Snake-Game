#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sense_hat import SenseHat
import time
import random
import os

# -----------------------------
# 可调参数（支持环境变量覆盖）
# -----------------------------
SNAKE_SPEED = float(os.getenv("SNAKE_SPEED", "0.15"))   # 菜单难度传入的速度（秒/步）
ALPHA       = float(os.getenv("ALPHA", "0.8"))          # 高通滤波系数
THRESHOLD   = float(os.getenv("THRESHOLD", "2.0"))      # 运动阈值（实机需调）
STEP_COOLD  = float(os.getenv("STEP_COOLDOWN", "0.50")) # 两次方向变更的冷却(秒)

COUNTDOWN_DELAY = 0.70
MATRIX_MIN_VALUE = 0
MATRIX_MAX_VALUE = 7
MATRIX_SIZE = 8

GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
NO_LED = (0, 0, 0)

senseHat = SenseHat()
senseHat.low_light = True
# 只开加速度计
senseHat.set_imu_config(True, False, False)

# -----------------------------
# 倒计时图案
# -----------------------------
def five_img():
    W, O = WHITE, NO_LED
    return [
        O, O, W, W, W, W, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, W, W, W, W, O, O,
    ]

def four_img():
    W, O = WHITE, NO_LED
    return [
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, W, O, O, O,
        O, O, W, W, W, W, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
    ]

def three_img():
    W, O = WHITE, NO_LED
    return [
        O, O, W, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, W, W, W, W, O, O,
    ]

def two_img():
    W, O = WHITE, NO_LED
    return [
        O, O, W, W, W, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, O, O, O, W, O, O,
        O, O, W, W, W, W, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, O, O, O, O, O,
        O, O, W, W, W, W, O, O,
    ]

def one_img():
    W, O = WHITE, NO_LED
    return [
        O, O, O, O, W, O, O, O,
        O, O, O, W, W, O, O, O,
        O, O, W, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, O, W, O, O, O,
        O, O, O, W, W, W, O, O,
    ]

images = [five_img, four_img, three_img, two_img, one_img]

# -----------------------------
# 步态/倾斜输入检测（高通 + 阈值 + 冷却）
# -----------------------------
last_x, last_y = 0.0, 0.0
last_fx, last_fy = 0.0, 0.0
last_step_time = time.time()

def get_movement():
    """
    从加速度计推断方向（右/左/下/上），
    返回 (dx, dy) 或 None（无新方向）。
    """
    global last_x, last_y, last_fx, last_fy, last_step_time

    accel = senseHat.get_accelerometer_raw()
    x = accel['x'] * 10.0
    y = accel['y'] * 10.0

    # 高通滤波
    fx = ALPHA * (last_fx + x - last_x)
    fy = ALPHA * (last_fy + y - last_y)

    last_x, last_y = x, y
    last_fx, last_fy = fx, fy

    now = time.time()
    if now - last_step_time > STEP_COOLD:
        if abs(fx) > abs(fy):
            if fx > THRESHOLD:
                last_step_time = now
                return (1, 0)   # 右
            elif fx < -THRESHOLD:
                last_step_time = now
                return (-1, 0)  # 左
        else:
            if fy > THRESHOLD:
                last_step_time = now
                return (0, 1)   # 下
            elif fy < -THRESHOLD:
                last_step_time = now
                return (0, -1)  # 上
    return None

# -----------------------------
# 主循环
# -----------------------------
while True:
    gameOverFlag = False
    growSnakeFlag = False
    generateRandomFoodFlag = False

    # 速度（可被难度覆盖）
    snakeMovementDelay = SNAKE_SPEED
    snakeMovementDelayDecrease = -0.02  # 吃果实加速

    # 开始倒计时
    for img in images:
        senseHat.set_pixels(img())
        time.sleep(COUNTDOWN_DELAY)

    # 初始位置与方向
    snakePosX = [3]
    snakePosY = [6]
    movementX, movementY = 0, -1  # 默认向上

    # 随机生成食物位置
    while True:
        foodPosX = random.randint(0, 7)
        foodPosY = random.randint(0, 7)
        if not (foodPosX == snakePosX[0] and foodPosY == snakePosY[0]):
            break

    # ------------- 游戏循环 -------------
    while not gameOverFlag:
        # 吃到食物
        if foodPosX == snakePosX[0] and foodPosY == snakePosY[0]:
            growSnakeFlag = True
            generateRandomFoodFlag = True
            snakeMovementDelay = max(0.03, snakeMovementDelay + snakeMovementDelayDecrease)

        # 自身碰撞
        for i in range(1, len(snakePosX)):
            if snakePosX[i] == snakePosX[0] and snakePosY[i] == snakePosY[0]:
                gameOverFlag = True
                break
        if gameOverFlag:
            break

        # 体感方向输入
        move = get_movement()
        if move:
            dx, dy = move
            # 禁止直接反向（掉头）：只有完全相反才禁止
            if not (dx == -movementX and dy == -movementY):
                movementX, movementY = dx, dy

        # 长度增长
        if growSnakeFlag:
            growSnakeFlag = False
            snakePosX.append(0)
            snakePosY.append(0)

        # 身体跟随
        for i in range(len(snakePosX) - 1, 0, -1):
            snakePosX[i] = snakePosX[i - 1]
            snakePosY[i] = snakePosY[i - 1]

        # 头部移动
        snakePosX[0] += movementX
        snakePosY[0] += movementY

        # 边界穿越（环面）
        if snakePosX[0] > MATRIX_MAX_VALUE:
            snakePosX[0] -= MATRIX_SIZE
        elif snakePosX[0] < MATRIX_MIN_VALUE:
            snakePosX[0] += MATRIX_SIZE
        if snakePosY[0] > MATRIX_MAX_VALUE:
            snakePosY[0] -= MATRIX_SIZE
        elif snakePosY[0] < MATRIX_MIN_VALUE:
            snakePosY[0] += MATRIX_SIZE

        # 重新生成食物（避免生成到蛇身上）
        if generateRandomFoodFlag:
            generateRandomFoodFlag = False
            while True:
                foodPosX = random.randint(0, 7)
                foodPosY = random.randint(0, 7)
                if all(not (x == foodPosX and y == foodPosY) for x, y in zip(snakePosX, snakePosY)):
                    break

        # 刷新显示
        senseHat.clear()
        senseHat.set_pixel(foodPosX, foodPosY, RED)
        for x, y in zip(snakePosX, snakePosY):
            senseHat.set_pixel(x, y, GREEN)

        # 帧间隔（难度/加速后的速度）
        time.sleep(snakeMovementDelay)
