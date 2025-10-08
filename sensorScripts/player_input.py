import time
from collections import deque
from .filteredAcceleration import get_filtered_acceleration, poll_readings

class PlayerInput:
    # PARAMETERS FOR FURTHER NOISE FILTERING
    SMOOTH_THRESHOLD = 0.065
    REQUIRED_READINGS = 7

    # SLIDING WINDOW PARAMETERS
    MAX_WINDOW_TIME = 0.7
    WEIGHT_RECENT = 1

    # STEP DETECTION
    MIN_STEP_INTERVAL = 0.4
    SETTLE_TIME = 0.15

    def __init__(self):
        self.last_step_time = 0.0
        self.movement_window_x = deque()  # stores (timestamp, x_value)
        self.movement_window_y = deque()  # stores (timestamp, y_value)
        self.step_in_progress_axis = {"x": False, "y": False}

    def _detect_axis_step(self, window, axis_name, now):
        if not self.step_in_progress_axis[axis_name] and any(abs(v) >= self.SMOOTH_THRESHOLD for t, v in window):
            self.step_in_progress_axis[axis_name] = True

        if self.step_in_progress_axis[axis_name]:
            # Step ends if last SETTLE_TIME readings are near zero
            settled = True
            for t, v in reversed(window):
                if now - t > self.SETTLE_TIME:
                    break
                if abs(v) >= self.SMOOTH_THRESHOLD:
                    settled = False
                    break

            if settled:
                xs = [v for t, v in window if v != 0.0]
                if len(xs) >= self.REQUIRED_READINGS:
                    weights = [1 + (i / len(xs)) * (self.WEIGHT_RECENT - 1) for i in range(len(xs))]
                    avg = sum(v * w for v, w in zip(xs, weights)) / sum(weights)
                    self.step_in_progress_axis[axis_name] = False
                    window.clear()
                    return avg
        return None

    def get_input(self):
        """
        Detects steps in X and Y axes and returns the dominant direction.
        Returns: None, "left", "right", "forwards", or "backwards"
        """
        now = time.time()
        poll_readings()
        acc = get_filtered_acceleration()
        x, y = acc['x'], acc['y']

        # Treat tiny movements as zero
        x = 0.0 if abs(x) < self.SMOOTH_THRESHOLD else x
        y = 0.0 if abs(y) < self.SMOOTH_THRESHOLD else y

        # Add readings to movement windows
        self.movement_window_x.append((now, x))
        self.movement_window_y.append((now, y))

        # Remove old readings beyond MAX_WINDOW_TIME
        while self.movement_window_x and (now - self.movement_window_x[0][0]) > self.MAX_WINDOW_TIME:
            self.movement_window_x.popleft()
        while self.movement_window_y and (now - self.movement_window_y[0][0]) > self.MAX_WINDOW_TIME:
            self.movement_window_y.popleft()

        # Cooldown check
        if (now - self.last_step_time) < self.MIN_STEP_INTERVAL:
            return None

        # Detect step for each axis
        avg_x = self._detect_axis_step(self.movement_window_x, "x", now)
        avg_y = self._detect_axis_step(self.movement_window_y, "y", now)

        # Determine dominant axis
        if avg_x is not None and (avg_y is None or abs(avg_x) >= abs(avg_y)):
            self.last_step_time = now
            return "right" if avg_x > 0 else "left"
        elif avg_y is not None:
            self.last_step_time = now
            return "backwards" if avg_y > 0 else "forwards"

        return None
