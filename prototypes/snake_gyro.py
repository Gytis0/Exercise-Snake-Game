import time, random, math
from sense_hat import SenseHat

sense = SenseHat()
sense.clear()

# ---- Game parameters ----
WIDTH, HEIGHT = 8, 8
snake = [(3, 3)]
snake_direction = "RIGHT"
food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
score = 0
snake_speed = 0.2  # seconds per move

# ---- Movement detection globals ----
pitch, roll = 0.0, 0.0
last_time = time.time()
STEP_THRESHOLD = 0.3

# Complementary filter parameter
alpha = 0.98

# Step cooldown to avoid multiple triggers
step_cooldown = 0.5
last_step_time = 0

def get_step_direction():
    global pitch, roll, last_time, last_step_time

    now = time.time()
    dt = now - last_time
    last_time = now

    accel = sense.get_accelerometer_raw()
    gyro = sense.get_gyroscope_raw()

    ax, ay, az = accel['x'], accel['y'], accel['z']
    gx, gy, gz = gyro['x'], gyro['y'], gyro['z']  # deg/sec

    # Integrate gyro
    roll += gx * dt
    pitch += gy * dt

    # Tilt from accelerometer
    acc_roll = math.atan2(ay, az)
    acc_pitch = math.atan2(-ax, math.sqrt(ay*ay + az*az))

    # Complementary filter
    roll = alpha * roll + (1 - alpha) * acc_roll
    pitch = alpha * pitch + (1 - alpha) * acc_pitch

    # Remove gravity
    gravity_x = math.sin(roll)
    gravity_y = -math.sin(pitch)
    gravity_z = math.cos(pitch) * math.cos(roll)

    x_f = ax - gravity_x
    y_f = ay - gravity_y

    # Step detection
    current_time = time.time()
    if current_time - last_step_time > step_cooldown:
        if abs(x_f) > abs(y_f):
            if x_f > STEP_THRESHOLD:
                last_step_time = current_time
                return "RIGHT"
            elif x_f < -STEP_THRESHOLD:
                last_step_time = current_time
                return "LEFT"
        else:
            if y_f > STEP_THRESHOLD:
                last_step_time = current_time
                return "DOWN"
            elif y_f < -STEP_THRESHOLD:
                last_step_time = current_time
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
        # Get step input
        move = get_step_direction()
        if move:
            # Prevent reversing
            if move == "UP" and snake_direction != "DOWN":
                snake_direction = "UP"
            elif move == "DOWN" and snake_direction != "UP":
                snake_direction = "DOWN"
            elif move == "LEFT" and snake_direction != "RIGHT":
                snake_direction = "LEFT"
            elif move == "RIGHT" and snake_direction != "LEFT":
                snake_direction = "RIGHT"

        # Move snake
        new_head = move_snake(snake_direction)

        # Check collision with self
        if new_head in snake:
            print("Game Over! Score:", score)
            break

        snake.insert(0, new_head)

        # Eating food
        if new_head == food:
            score += 1
            while food in snake:
                food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        else:
            snake.pop()

        # Draw frame
        draw()
        time.sleep(snake_speed)

except KeyboardInterrupt:
    sense.clear()

