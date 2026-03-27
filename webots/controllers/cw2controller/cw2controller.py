from controller import Robot, Camera

MAX_SPEED = 6.28
MULTIPLIER = 0.5
OBSTACLE_DISTANCE = 0.02

DOMINANCE_MARGIN = 60

MIN_INTENSITY = 120


# ================= HELPER FUNCTIONS =================
def get_distance_values(distance_sensors, distance_values):
    for i in range(8):
        val = distance_sensors[i].getValue() / 4096.0
        distance_values[i] = min(val, 1.0)


def front_obstacle(distance_values):
    avg = (distance_values[0] + distance_values[7]) / 2.0
    return avg > OBSTACLE_DISTANCE


def move_forward(left_motor, right_motor):
    left_motor.setVelocity(MAX_SPEED * MULTIPLIER)
    right_motor.setVelocity(MAX_SPEED * MULTIPLIER)


def move_backward(left_motor, right_motor, robot, timestep):
    left_motor.setVelocity(-MAX_SPEED * MULTIPLIER)
    right_motor.setVelocity(-MAX_SPEED * MULTIPLIER)
    wait(robot, timestep, 0.3)


def turn_left(left_motor, right_motor, robot, timestep):
    left_motor.setVelocity(-MAX_SPEED * MULTIPLIER)
    right_motor.setVelocity(MAX_SPEED * MULTIPLIER)
    wait(robot, timestep, 0.3)


def wait(robot, timestep, sec):
    start = robot.getTime()
    while robot.getTime() < start + sec:
        robot.step(timestep)


def get_camera_rgb(camera, interval, state):
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()

    if state["camera_interval"] >= interval:
        r = g = b = 0
        for x in range(width):
            for y in range(height):
                r += camera.imageGetRed(image, width, x, y)
                g += camera.imageGetGreen(image, width, x, y)
                b += camera.imageGetBlue(image, width, x, y)

        state["camera_interval"] = 0
        return (
            int(r / (width * height)),
            int(g / (width * height)),
            int(b / (width * height)),
        )
    else:
        state["camera_interval"] += 1
        return (0, 0, 0)


# ================= MAIN ROBOT FUNCTION =================
def run_robot(robot):
    timestep = int(robot.getBasicTimeStep())

    # ----- Distance sensors -----
    sensor_names = ("ps0",
                    "ps1",
                    "ps2",
                    "ps3",
                    "ps4",
                    "ps5",
                    "ps6",
                    "ps7")
                    
    distance_sensors = []
    distance_values = [0.0] * 8

    for name in sensor_names:
        s = robot.getDevice(name)
        s.enable(timestep)
        distance_sensors.append(s)

    # ----- Camera -----
    camera = robot.getDevice("camera")
    camera.enable(timestep)
    camera_state = {"camera_interval": 0}

    # ----- Motors -----
    left_motor = robot.getDevice("left wheel motor")
    right_motor = robot.getDevice("right wheel motor")

    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))

    encountered = []  # Students may use this later

    # ================= MAIN LOOP =================
    while robot.step(timestep) != -1:

        # --- Sensors ---
        get_distance_values(distance_sensors, distance_values)
        red, green, blue = get_camera_rgb(camera, 5, camera_state)
        
     
        # -------- COLOR DETECTION AND REPORTING --------
        if not (red == 0 and green == 0 and blue == 0):
            detected_color = None
       
            # Red and Green usually work well with standard margins
            if red > MIN_INTENSITY and red - max(green, blue) > DOMINANCE_MARGIN:
                detected_color = "red"
            elif green > MIN_INTENSITY and green - max(red, blue) > DOMINANCE_MARGIN:
                detected_color = "green"
            elif blue > MIN_INTENSITY and blue - max(red, green) > DOMINANCE_MARGIN:
                detected_color = "blue"

            if detected_color and detected_color not in encountered:
                print(f"I see {detected_color}")
                encountered.append(detected_color)
                print(f"I have seen {', '.join(encountered)}")


        # -------- OBSTACLE AVOIDANCE --------
        if front_obstacle(distance_values):
            move_backward(left_motor, right_motor, robot, timestep)
            turn_left(left_motor, right_motor, robot, timestep)
        else:
            move_forward(left_motor, right_motor)


# ================= ENTRY POINT =================
if __name__ == "__main__":
    my_robot = Robot()
    run_robot(my_robot)