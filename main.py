#!/usr/bin/env python3
from sense_hat import SenseHat
import time, subprocess, os
from remind import should_show_notification, show_notification, update_last_play_time

# 用"模块名"而不是文件路径
MODES = [
    ("TILT", "prototypes.snake_tilt"),
    ("GYRO", "prototypes.snake_gyro"),
    ("HPF",  "prototypes.snake_highpassFilter"),
    ("STEP", "prototypes.snake_step"),
    ("CXLT", "prototypes.snake_cancel_tilt"),
]

SPEEDS = [("EASY", "0.25"), ("NORM", "0.15"), ("HARD", "0.08")]

sense = SenseHat()
sense.low_light = True
sense.clear()

# Check if notification should be shown (24 hours since last play)
if should_show_notification():
    show_notification(sense)

def show(text):
    sense.show_message(text, scroll_speed=0.06, text_colour=[0,255,0])

def choose(items, title):
    idx = 0
    show(title + ":" + items[idx][0])
    while True:
        for e in sense.stick.get_events():
            if e.action != "pressed": 
                continue
            if e.direction in ("right","up"):
                idx = (idx + 1) % len(items); show(items[idx][0])
            if e.direction in ("left","down"):
                idx = (idx - 1) % len(items); show(items[idx][0])
            if e.direction == "middle":
                return items[idx]

def main():
    mode_name, module_name = choose(MODES, "INPUT")
    speed_name, speed_val   = choose(SPEEDS, "SPEED")
    show(f"GO {mode_name}-{speed_name}")

    # Update last play timestamp when game starts
    update_last_play_time()

    env = os.environ.copy()
    env["SNAKE_SPEED"] = speed_val

    # 关键：以"模块"方式运行，保证包导入可用
    subprocess.run(
        ["/usr/bin/env", "python3", "-m", module_name],
        cwd=os.path.dirname(__file__),
        env=env,
        check=False
    )
    sense.clear()

if __name__ == "__main__":
    main()
