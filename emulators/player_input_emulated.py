import keyboard  # pip install keyboard
import time

class PlayerInputEmulated:
    def __init__(self):
        self._last_input = None

    def get_input(self):
        """
        Returns one of: "right", "left", "forwards", "backwards"
        based on W/A/S/D keys.
        """
        if keyboard.is_pressed('w'):
            return "forwards"
        elif keyboard.is_pressed('s'):
            return "backwards"
        elif keyboard.is_pressed('a'):
            return "left"
        elif keyboard.is_pressed('d'):
            return "right"
        elif keyboard.is_pressed('esc'):
            print("Exiting game...")
            time.sleep(0.1)
            import os
            os._exit(0)
        else:
            return None
