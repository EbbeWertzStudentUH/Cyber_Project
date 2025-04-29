from controller import Robot, Camera
from kinematic import RobotKinematic
import math

TIME_STEP = 32
robot = Robot()
kinematic = RobotKinematic.getInstance()

lidar = robot.getDevice("lidar")
lidar.enable(TIME_STEP)
lidar.enablePointCloud()

wheels = []
for name in ["wheel1", "wheel2", "wheel3", "wheel4"]:
    motor = robot.getDevice(name)
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)
    wheels.append(motor)

camera = robot.getDevice('color_sensor')
camera.enable(TIME_STEP)

def set_wheel_speeds(vx, vy, omega, kinematic):
    motion = kinematic.inversKinematic(vx, vy, omega)
    wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]
    for i in range(4):
        wheels[i].setVelocity(wheel_speeds[i])

def detect_white_position():
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()

    white_pixels = []

    for y in range(height):
        for x in range(width):
            if not (width * 0.15 <= x <= width * 0.85 and height * 0.15 <= y <= height * 0.85):
                continue  # Sla deze pixel over

            r = Camera.imageGetRed(image, width, x, y)
            g = Camera.imageGetGreen(image, width, x, y)
            b = Camera.imageGetBlue(image, width, x, y)

            if r < 10 and g < 10 and b < 10:
                white_pixels.append((x, y))

    if not white_pixels:
        return None

    avg_x = sum(p[0] for p in white_pixels) / len(white_pixels)
    avg_y = sum(p[1] for p in white_pixels) / len(white_pixels)

    return avg_x / width, avg_y / height  # genormaliseerd naar 0..1

def zoek_en_centreer_op_bol():
    while robot.step(TIME_STEP) != -1:
        kinematic.updateOdometry()

        pos = detect_white_position()

        if pos is None:
            break  # Stop als geen bol

        avg_x, avg_y = pos

        error_x = avg_x - 0.5
        error_y = avg_y - 0.5
        
        vx = 0.0
        vy = 0.0

        if abs(error_y) > 0.01:
            vx = -0.1 if error_y > 0 else 0.1  # naar links of rechts

        if abs(error_x) > 0.01:
            vy = -0.1 if error_x > 0 else 0.1  # naar links of rechts

        if abs(error_x) <= 0.05 and abs(error_y) <= 0.05:
            break

        set_wheel_speeds(vx, vy, 0.0, kinematic)

    for i in range(4):
        wheels[i].setVelocity(0.0)

def rijdt(richting_rad, afstand):
    snelheid = 0.2  # constante snelheid (m/s)
    vx = snelheid * math.cos(richting_rad)
    vy = snelheid * math.sin(richting_rad)
    omega = 0.0

    pos = kinematic.getPos()
    initial_pos = type(pos)(pos.x, pos.y, pos.theta)

    target_x = initial_pos.x + afstand * math.cos(richting_rad)
    target_y = initial_pos.y + afstand * math.sin(richting_rad)

    tolerance = 0.01

    while True:
        if robot.step(TIME_STEP) == -1:
            break

        kinematic.updateOdometry()

        ranges = lidar.getRangeImage()
        if any(distance < 0.5 for distance in ranges):
            print("⚠️ Obstacle within 50 cm — stopping robot!")
            for wheel in wheels:
                wheel.setVelocity(0.0)
            return  # stop direct
        else: print("clear path")

        current_pos = kinematic.getPos()
        dx = current_pos.x - initial_pos.x
        dy = current_pos.y - initial_pos.y
        distance_travelled = math.sqrt(dx**2 + dy**2)

        if distance_travelled >= afstand - tolerance:
            break

        set_wheel_speeds(vx, vy, omega, kinematic)

    for i in range(4):
        wheels[i].setVelocity(0.0)

# --- Gebruik ---
rijdt(math.pi, 4.0)
rijdt(-math.pi/2, 1.0)

while robot.step(TIME_STEP) != -1:
    kinematic.updateOdometry()

    if detect_white_position() is not None:
        zoek_en_centreer_op_bol()

    for i in range(4):
        wheels[i].setVelocity(0.0)
