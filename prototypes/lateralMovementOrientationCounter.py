#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A minimal orientation-compensation helper for snake_highpassFilter.py
import os, time, math
from sense_hat import SenseHat

# 可调：互补滤波系数
ALPHA = float(os.getenv("ALPHA", "0.98"))

sense = SenseHat()
# 同时启用加速度计与陀螺仪（不启用磁力计）
sense.set_imu_config(True, True, False)

# 内部状态
_last_t = time.time()
_roll = 0.0
_pitch = 0.0
_last_af = {"x": 0.0, "y": 0.0, "z": 0.0}

def poll_readings():
    """
    更新内部状态（互补滤波估计姿态），并计算去倾斜后的加速度分量。
    """
    global _last_t, _roll, _pitch, _last_af

    now = time.time()
    dt = now - _last_t if _last_t else 0.0
    _last_t = now

    a = sense.get_accelerometer_raw()
    g = sense.get_gyroscope_raw()

    ax, ay, az = a["x"], a["y"], a["z"]
    gx, gy = g["x"], g["y"]  # 角速度

    # 互补滤波：陀螺积分 + 加速度角纠偏
    _roll  += gx * dt
    _pitch += gy * dt

    acc_roll  = math.atan2(ay, az)
    acc_pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))

    _roll  = ALPHA * _roll  + (1.0 - ALPHA) * acc_roll
    _pitch = ALPHA * _pitch + (1.0 - ALPHA) * acc_pitch

    # 去除重力分量（近似）
    g_x = math.sin(_roll)
    g_y = -math.sin(_pitch)
    g_z = math.cos(_pitch) * math.cos(_roll)

    _last_af = {
        "x": ax - g_x,
        "y": ay - g_y,
        "z": az - g_z,
    }

def get_acceleration_without_tilt():
    """
    返回最近一次 poll_readings() 计算的去倾斜加速度分量。
    """
    return _last_af

