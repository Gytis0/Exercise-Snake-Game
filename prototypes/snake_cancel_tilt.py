#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sense_hat import SenseHat
import math
import time
import random
import os

# -------------------------------
# 可调参数（环境变量覆盖）
# -------------------------------
SNAKE_SPEED = float(os.getenv("SNAKE_SPEED", "0.15"))   # 难度速度：秒/步
THRESHOLD   = float(os.getenv("THRESHOLD", "0.25"))     # 触发阈值（g）
POLL_RATE   = float(os.getenv("POLL_RATE", "0.01"))     # 轮询间隔（秒）

# -------------------------------
# Setup
# -------------------------------
sense = SenseHat()
sense.low_light = True
# 为了 orientation 融合稳定，开启三轴（若想省电可改为 True, True, False 关闭磁力计）
sense.set_imu_config(True, True, True)

# Colors
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
COUNTDOWN_DELAY  = 0.7
MATRIX_MIN_VALUE = 0
MATRIX_MAX_VALUE = 7
MATRIX_SIZE      = 8

# -------------------------------
# Accelerometer / Movement
# -------------------------------
cached_pitch = 0.0
cached_roll  = 0.0
cached_x = 0.0
cached_y = 0.0
cached_z = 0.0
_time_last = 0.0

def poll_readings():
    """按 POLL_RATE 节流读取 IMU，并缓存 pitch/roll 与加速度原始值"""
    global cached_pitch, cached_roll, cached_x, cached_y, cached_z, _time_last
    now = time.time()
    if now - _time_last >= POLL_RATE:
        # orientation_degrees: 需要 IMU 融合
        orientation = sense.get_orientation_degrees()
        cached_pitch = math.radians(orientation['pitch'])
        cached_roll  = math.radians(orientation['roll'])

        a = sense.get_accelerometer_raw()
        cached_x, cached_y, cached_z = a['x'], a['y'], a['z']
        _time_last = now

def get_acceleration_without_tilt():
    """用估计的姿态角去除重力分量，返回“去倾斜后的”加速度分量"""
    gravity_x = -math.sin(cached_pitch)
    gravity_y =  math.sin(cached_roll)
    gravity_z = -math.cos(cached_pitch) * math.cos(cached_roll)

    ax_true = cached_x - gravity_x
    ay_true = cached_y - gravity_y
    az_true = cached_z - gravity_z
    return {'x': ax_true, 'y': ay_true, 'z': az_true}

def get_movement_tilt_corrected():
    """基于去倾斜加速度的方向判定，返回 (dx,dy) 或 None"""
    poll_readings()
    acc = get_acceleration_without_tilt()

    if abs(acc['x']) > abs(acc['y']):
        if acc['x'] > THRESHOLD:
            return (1, 0)    # right
        elif acc['x'] < -THRESHOLD:
            return (-1, 0)   # left
    else:
        if acc['y'] > THRESHOLD:
            return (0, 1)    # down
        elif acc['y'] < -THRESHOLD:
            return (0, -1)   # up
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
    movementX, movementY = 0, -1

    # Food setup（不与蛇头重叠）
    while True:
        foodPosX = random.randint(0, 7)
        foodPosY = random.randint(0, 7)
        if (foodPosX, foodPosY) != (snakePosX[0], snakePosY[0]):
            break

    snakeMovementDelay = SNAKE_SPEED         # ← 使用难度速度
    snakeMovementDelayDecrease = -0.02       # 吃到食物后加速
    gameOverFlag = False
    growSnakeFlag = False

    while not gameOverFlag:
        # 吃到食物：增长+加速
        if (foodPosX, foodPosY) == (snakePosX[0], snakePosY[0]):
            growSnakeFlag = True
            # 重新生成食物（不与蛇身重叠）
            while True:
                foodPosX = random.randint(0, 7)
                foodPosY = random.randint(0, 7)
                if all((x, y) != (foodPosX, foodPosY) for x, y in zip(snakePosX, snakePosY)):
                    break
            snakeMovementDelay = max(0.03, snakeMovementDelay + snakeMovementDelayDecrease)

        # 自身碰撞
        for i in range(1, len(snakePosX)):
            if (snakePosX[i], snakePosY[i]) == (snakePosX[0], snakePosY[0]):
                gameOverFlag = True
                break
        if gameOverFlag:
            break

        # 检测方向
        move = get_movement_tilt_corrected()
        if move:
            dx, dy = move
            # 禁止直接反向（仅当完全相反时禁掉）
            if not (dx == -movementX and dy == -movementY):
                movementX, movementY = dx, dy

        # 变长
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

        # 环绕边界
        snakePosX[0] %= MATRIX_SIZE
        snakePosY[0] %= MATRIX_SIZE

        # 渲染
        sense.clear()
        sense.set_pixel(foodPosX, foodPosY, RED)
        for x, y in zip(snakePosX, snakePosY):
            sense.set_pixel(x, y, GREEN)

        time.sleep(snakeMovementDelay)

except KeyboardInterrupt:
    pass
finally:
    sense.clear()
    print("\nGame stopped.")
