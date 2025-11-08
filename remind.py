#!/usr/bin/env python3
"""
Notification system for Snake Game
Tracks last play time and shows notification if game wasn't played in 23 hours
"""
import json
import os
import time

LAST_PLAY_FILE = "last_play.json"
NOTIFICATION_COOLDOWN_HOURS = 24


def get_last_play_time():
    """Get the last play timestamp from file, or None if file doesn't exist"""
    if not os.path.exists(LAST_PLAY_FILE):
        return None

    try:
        with open(LAST_PLAY_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_play_timestamp')
    except (json.JSONDecodeError, KeyError, IOError):
        return None


def update_last_play_time():
    """Update the last play timestamp to current time"""
    data = {
        'last_play_timestamp': time.time()
    }
    try:
        with open(LAST_PLAY_FILE, 'w') as f:
            json.dump(data, f)
    except IOError:
        pass  # Silently fail if we can't write


def should_show_notification():
    """Check if notification should be shown (24 hours since last play)"""
    last_play = get_last_play_time()

    if last_play is None:
        # First time playing, show notification
        return True

    time_since_last_play = time.time() - last_play
    hours_since_last_play = time_since_last_play / 3600

    return hours_since_last_play >= NOTIFICATION_COOLDOWN_HOURS


def flash_led_grid(sense_hat, times=3, flash_color=(255, 255, 255), flash_duration=0.2):
    """
    Flash the LED grid a few times

    Args:
        sense_hat: SenseHat instance
        times: Number of times to flash
        flash_color: RGB color tuple for flash
        flash_duration: Duration of each flash in seconds
    """
    # Create a full grid of the flash color
    flash_pixels = [flash_color] * 64

    for _ in range(times):
        # Flash on
        sense_hat.set_pixels(flash_pixels)
        time.sleep(flash_duration)
        # Flash off
        sense_hat.clear()
        time.sleep(flash_duration)


def show_notification(sense_hat):
    """
    Show the notification: flash LED grid and display "time to play" message

    Args:
        sense_hat: SenseHat instance
    """
    # Flash the LED grid a few times
    flash_led_grid(sense_hat, times=3, flash_color=(255, 255, 0), flash_duration=0.15)

    # Show "time to play" message
    sense_hat.show_message("PLAY", scroll_speed=0.07, text_colour=[255, 255, 0])

    # Clear after message
    sense_hat.clear()
    time.sleep(0.5)

