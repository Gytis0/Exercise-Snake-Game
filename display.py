from images import images
import time

class Display:
    COUNTDOWN_DELAY = 0.5
    
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_GREEN_LIGHT = (0, 100, 0)
    COLOR_YELLOW = (255, 255, 0)
    
    def __init__(self, sense_hat):
        """
        sense_hat: instance of SenseHatEmulated
        """
        self.sense_hat = sense_hat

        self.head_color = self.COLOR_GREEN
        self.tail_color = self.COLOR_YELLOW
        self.food_color = self.COLOR_RED

    def get_current_frame(self, snakePosX, snakePosY, foodPosX, foodPosY, snake_color=(0, 255, 0), food_color=(255, 0, 0)):
        """
        Returns the current frame as a flat list of 64 RGB tuples
        with the snake and food drawn on it.
        """
        frame = [(0, 0, 0)] * 64 

        for x, y in zip(snakePosX, snakePosY):
            if 0 <= x < 8 and 0 <= y < 8:
                frame[y * 8 + x] = snake_color

        if 0 <= foodPosX < 8 and 0 <= foodPosY < 8:
            frame[foodPosY * 8 + foodPosX] = food_color

        return frame
    
    def update_snake(self, snake_positionsX, snake_positionsY):
        """
        snake_positions: list of (x, y) tuples
        Draws snake with gradient from head to tail
        """
        snake_positions = list(zip(snake_positionsX, snake_positionsY))
        n = len(snake_positions)
        for idx, (x, y) in enumerate(snake_positions):
            if n == 1:
                color = self.head_color
            else:
                ratio = idx / (n - 1)
                color = self._interpolate_color(self.head_color, self.tail_color, ratio)
            self.sense_hat.set_pixel(x, y, color)

    def draw_food(self, x, y):
        self.sense_hat.set_pixel(x, y, self.food_color)

    def clear(self):
        self.sense_hat.clear()
        
    def showCountdown(self, background_pixels=None):
        for img in images:
            if background_pixels:
                merged = []
                countdown_img = img()
                for b_pixel, c_pixel in zip(background_pixels, countdown_img):
                    merged.append(c_pixel if c_pixel != (0, 0, 0) else b_pixel)
                self.sense_hat.set_pixels(merged)
            else:
                self.sense_hat.set_pixels(img())
            time.sleep(self.COUNTDOWN_DELAY)


    def _interpolate_color(self, start_color, end_color, ratio):
        """Linear interpolation for gradient color"""
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        return (r, g, b)
