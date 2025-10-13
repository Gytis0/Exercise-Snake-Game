#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import random
import math
from sense_hat import SenseHat

# -----------------------------
# 可调参数（支持环境变量覆盖）
# -----------------------------
SNAKE_SPEED     = float(os.getenv("SNAKE_SPEED", "0.15"))  # 菜单传入的速度（秒/步）
ALPHA           = float(os.getenv("ALPHA", "0.98"))        # 互补滤波系数
STEP_THRESHOLD  = float(os.getenv("STEP_THRESHOLD", "0.3"))# 触发阈值（实机需调）
STEP_COOLDOWN   = float(os.getenv("STEP_COOLDOWN", "0.5")) # 两次方向变更冷却(秒)

# -----------------------------
# 初始化
# -----------------------------
sense = SenseHat()
sense.low_light = True
# 同时启用加速度计与陀螺仪（不启用磁力计）
sense.set_imu_config(True, True, False)
sense.clear()

# ---- Game parameters ----
WIDTH, HEIGHT = 8, 8
snake = [(3, 3)]
snake_direction = "RIGHT"
food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
score = 0
snake_speed = SNAKE_SPEED  # seconds per move（支持难度）

# ---- Movement detection globals ----
pitch, roll = 0.0, 0.0
last_time = time.time()
last_step_time = 0.0

def get_step_direction():
    """利用加速度计+陀螺仪（互补滤波）推断方向，返回UP/DOWN/LEFT/RIGHT或None"""
    global pitch, roll, last_time, last_step_time

    now = time.time()
    dt = now - last_time if last_time else 0.0
    last_time = now

    # 读取原始传感器
    accel = sense.get_accelerometer_raw()
    gyro  = sense.get_gyroscope_raw()

    ax, ay, az = accel['x'], accel['y'], accel['z']
    gx, gy, gz = gyro['x'],  gyro['y'],  gyro['z']   # 注意：sense_hat返回的是角速度（单位依固件实现）

    # --- 互补滤波 ---
    # 1) 积分陀螺得到角度增量
    roll  += gx * dt
    pitch += gy * dt

    # 2) 由加速度估计倾角（抗漂移）
    acc_roll  = math.atan2(ay, az)
    acc_pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))

    # 3) 融合
    roll  = ALPHA * roll  + (1.0 - ALPHA) * acc_roll
    pitch = ALPHA * pitch + (1.0 - ALPHA) * acc_pitch

    # 重力分量估计并去除（简化）
    gravity_x = math.sin(roll)
    gravity_y = -math.sin(pitch)
    # gravity_z = math.cos(pitch) * math.cos(roll)  # 未使用

    # 高通后的加速度（近似运动分量）
    x_f = ax - gravity_x
    y_f = ay - gravity_y

    # 冷却：避免一次动作触发多次
    if now - last_step_time > STEP_COOLDOWN:
        if abs(x_f) > abs(y_f):
            if x_f > STEP_THRESHOLD:
                last_step_time = now
                return "RIGHT"
            elif x_f < -STEP_THRESHOLD:
                last_step_time = now
                return "LEFT"
        else:
            if y_f > STEP_THRESHOLD:
                last_step_time = now
                return "DOWN"
            elif y_f < -STEP_THRESHOLD:
                last_step_time = now
                return "UP"

    return None

def draw():
    sense.clear()
    for x, y in snake:
        sense.set_pixel(x, y, (0, 255, 0))
    sense.set_pixel(food[0], food[1], (255, 0, 0))

def move_snake(direction):
    head_x, head_y = snake[0]
    if direction == "UP":
        head_y -= 1
    elif direction == "DOWN":
        head_y += 1
    elif direction == "LEFT":
        head_x -= 1
    elif direction == "RIGHT":
        head_x += 1
    return (head_x % WIDTH, head_y % HEIGHT)

# ---- Main game loop ----
try:
    while True:
        # 体感输入
        move = get_step_direction()
        if move:
            # 禁止直接反向
            if move == "UP" and snake_direction != "DOWN":
                snake_direction = "UP"
            elif move == "DOWN" and snake_direction != "UP":
                snake_direction = "DOWN"
            elif move == "LEFT" and snake_direction != "RIGHT":
                snake_direction = "LEFT"
            elif move == "RIGHT" and snake_direction != "LEFT":
                snake_direction = "RIGHT"

        # 前进一步
        new_head = move_snake(snake_direction)

        # 撞到自己 → Game Over
        if new_head in snake:
            # 这里不使用show_message避免阻塞；需要可换为 sense.show_message(str)
            print("Game Over! Score:", score)
            break

        snake.insert(0, new_head)

        # 吃到食物
        if new_head == food:
            score += 1
            # 重新生成不与蛇身重叠的位置
            while True:
                nf = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
                if nf not in snake:
                    food = nf
                    break
            # 可选：随分数微调速度
            # snake_speed = max(0.05, snake_speed - 0.01)
        else:
            snake.pop()

        # 刷新显示
        draw()
        time.sleep(snake_speed)

except KeyboardInterrupt:
    pass
finally:
    sense.clear()
