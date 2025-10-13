#!/usr/bin/env python3
from sense_hat import SenseHat
import time

s = SenseHat()
s.clear()
s.show_message("PLAY", scroll_speed=0.07, text_colour=[255,255,0])
time.sleep(1)
s.clear()
