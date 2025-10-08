import os

class SenseHatEmulated:
    NO_LED = (0, 0, 0)

    def __init__(self):
        self.matrix = [[self.NO_LED for _ in range(8)] for _ in range(8)]

    def clear(self):
        self.matrix = [[self.NO_LED for _ in range(8)] for _ in range(8)]
        self._draw_matrix()

    def set_pixel(self, x, y, color):
        if 0 <= x < 8 and 0 <= y < 8:
            self.matrix[y][x] = color
        self._draw_matrix()

    def set_pixels(self, pixels):
        if len(pixels) != 64:
            raise ValueError("Pixels must be a list of 64 (R,G,B) tuples.")
        self.matrix = [pixels[i*8:(i+1)*8] for i in range(8)]
        self._draw_matrix()

    def _draw_matrix(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("┌" + "─"*16 + "┐")
        for row in self.matrix:
            line = "│"
            for (r, g, b) in row:
                if (r, g, b) == self.NO_LED:
                    line += "  "
                else:
                    line += f"\033[38;2;{r};{g};{b}m██\033[0m"
            line += "│"
            print(line)
        print("└" + "─"*16 + "┘")
