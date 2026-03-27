from controller import Robot, Motor, DistanceSensor, Camera



# ================= CONSTANTS =================

MAX_SPEED = 6.28

MULTIPLIER = 0.5

OBSTACLE_DISTANCE = 0.02



# --- UPDATED: Cat RGB values and Tolerance ---

# Note: You may need to check the 'Display' or 'Camera' view in Webots 

# to get the exact RGB of your cat. These are common starting values.

CAT_R, CAT_G, CAT_B = 100, 100, 100 

TOLERANCE = 50



# RGB Color detection thresholds

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



def get_average_rgb(camera):

    width = camera.getWidth()

    height = camera.getHeight()

    image = camera.getImage()

    

    r = g = b = 0

    for x in range(width):

        for y in range(height):

            r += camera.imageGetRed(image, width, x, y)

            g += camera.imageGetGreen(image, width, x, y)

            b += camera.imageGetBlue(image, width, x, y)

            

    num_pixels = width * height

    return int(r / num_pixels), int(g / num_pixels), int(b / num_pixels)



# --- UPDATED: Cat Detection Logic ---

def is_cat(r, g, b):

    """Checks if the current RGB matches the Cat's profile."""

    return (abs(r - CAT_R) < TOLERANCE and

            abs(g - CAT_G) < TOLERANCE and

            abs(b - CAT_B) < TOLERANCE)



# ================= MAIN ROBOT FUNCTION =================



def run_robot(robot):

    timestep = int(robot.getBasicTimeStep())



    sensor_names = ["ps0","ps1","ps2","ps3","ps4","ps5","ps6","ps7"]

    distance_sensors = []

    distance_values = [0.0] * 8



    for name in sensor_names:

        s = robot.getDevice(name)

        s.enable(timestep)

        distance_sensors.append(s)



    camera = robot.getDevice("camera")

    camera.enable(timestep)



    left_motor = robot.getDevice("left wheel motor")

    right_motor = robot.getDevice("right wheel motor")

    left_motor.setPosition(float('inf'))

    right_motor.setPosition(float('inf'))

    left_motor.setVelocity(0)

    right_motor.setVelocity(0)



    encountered = []

    image_counter = 0

    camera_tick = 0

    CAMERA_INTERVAL = 5 



    while robot.step(timestep) != -1:

        get_distance_values(distance_sensors, distance_values)



        if camera_tick >= CAMERA_INTERVAL:

            r, g, b = get_average_rgb(camera)

            detected_color = None



            # --- UPDATED: Check for CAT first ---

            if is_cat(r, g, b):

                detected_color = "cat"

                if "cat" not in encountered:

                    left_motor.setVelocity(0)

                    right_motor.setVelocity(0)

                    # UPDATED: Filename changed to cat

                    filename = f"cat_capture_{image_counter}.png"

                    camera.saveImage(filename, 100)

                    print(f"Captured {filename}")

                    image_counter += 1

            

            elif r > MIN_INTENSITY and r - max(g, b) > DOMINANCE_MARGIN:

                detected_color = "red"

            elif g > MIN_INTENSITY and g - max(r, b) > DOMINANCE_MARGIN:

                detected_color = "green"

            elif b > MIN_INTENSITY and b - max(r, g) > DOMINANCE_MARGIN:

                detected_color = "blue"



            if detected_color and detected_color not in encountered:

                print(f"I see {detected_color}")

                encountered.append(detected_color)

                print(f"I have seen: {', '.join(encountered)}")



            camera_tick = 0

        else:

            camera_tick += 1



        if front_obstacle(distance_values):

            move_backward(left_motor, right_motor, robot, timestep)

            turn_left(left_motor, right_motor, robot, timestep)

        else:

            move_forward(left_motor, right_motor)



if __name__ == "__main__":

    my_robot = Robot()

    run_robot(my_robot)