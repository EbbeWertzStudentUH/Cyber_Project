from dacite import from_dict
from controller import Robot, Camera, Display
from kinematic import RobotKinematic
import math
import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass
from datetime import datetime
import threading
from pydantic_core import from_json, to_json
from command_types import MovementCommand, PanicResponse, MoveArriveResponse, PickupResponse, \
    DropOffResponse, PickupCommand, DropOffCommand
    
from queue import Queue
task_queue = Queue()


TIME_STEP = 16
robot = Robot()
kinematic = RobotKinematic.getInstance()
robot_id = robot.getName()
print(f"Controller started for robot {robot_id}")
broker = "localhost"
port = 1883

hasPackage = False

inertial_unit = robot.getDevice("IMU")
inertial_unit.enable(TIME_STEP)


# Apparaten instellen
lidar = robot.getDevice("lidar")
lidar.enable(TIME_STEP)
lidar.enablePointCloud()

compass = robot.getDevice("compass")
compass.enable(TIME_STEP)

wheels = []
for name in ["wheel1", "wheel2", "wheel3", "wheel4"]:
    motor = robot.getDevice(name)
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)
    wheels.append(motor)
    

    
print("waiting for compass to work...")
while robot.step(TIME_STEP) != -1:
    compass_values = compass.getValues()
    if not any(math.isnan(v) for v in compass_values):
        break  # compass is now ready
    
compass_values = compass.getValues()
print(f"Compass values: {compass_values}")
kinpos = kinematic.getPos()
print(f"Before compass: pos = x:{kinpos.x} y:{kinpos.y} t:{kinpos.theta}")

# goal_heading = math.atan2(compass_values[0], compass_values[2]) # robot compass direction to keep correcting towards
goal_heading = inertial_unit.getRollPitchYaw()[2]

camera = robot.getDevice('color_sensor')

display = robot.getDevice("camera_display")


camera.enable(TIME_STEP)

# Snelheden toepassen (en houdt de orientatie recht)
def set_wheel_speeds(vx, vy, omega, kinematic):
    motion = kinematic.inversKinematic(vx, vy, omega)
    wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]
    for i in range(4):
        wheels[i].setVelocity(wheel_speeds[i])
        
def pickup():
    global hasPackage
    hasPackage = True
    wait_time = 1.0
    start_time = robot.getTime()
    while robot.getTime() - start_time < wait_time:
        kinematic.updateOdometry()
        set_wheel_speeds(0.0, 0.0, 0.0, kinematic)
        robot.step(TIME_STEP)  # <- Advance simulation time!
    for i in range(4):
        wheels[i].setVelocity(0.0)


def drop_off():
    global hasPackage
    hasPackage = False
    wait_time = 1.0
    start_time = robot.getTime()
    while robot.getTime() - start_time < wait_time:
        kinematic.updateOdometry()
        set_wheel_speeds(0.0, 0.0, 0.0, kinematic)
        robot.step(TIME_STEP)  # <- Advance simulation time!
    for i in range(4):
        wheels[i].setVelocity(0.0)

# Bol detecteren
def draw_centroid_marker(x, y, black_pixels):
    width = camera.getWidth()
    height = camera.getHeight()

    # Create a blank RGBA mask image
    mask = bytearray([0] * (width * height * 4))  # RGBA = 4 channels

    # Set blue pixels (or any color) at black pixel locations
    for px, py in black_pixels:
        i = (py * width + px) * 4
        mask[i] = 0      # R
        mask[i + 1] = 255  # G
        mask[i + 2] = 255  # B
        mask[i + 3] = 255  # A (fully opaque)

    # Create a reference to the current camera image
    image = camera.getImage()
    image_ref = display.imageNew(image, Display.RGBA, width, height)
    display.imagePaste(image_ref, 0, 0, False)

    # Create and paste the mask image
    mask_ref = display.imageNew(bytes(mask), Display.RGBA, width, height)
    display.imagePaste(mask_ref, 0, 0, True)  # Alpha blending ON

    # Draw centroid marker (red dot)
    display.setColor(0xFF0000)
    display.fillOval(int(x - 2), int(y - 2), 4, 4)


def detect_black_position():
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()

    # Center and radius of the usable circle view (corners of camera view have wheel shadows)
    center_x = width / 2
    center_y = height / 2
    radius = min(width, height) / 2 - 3  # 3 pixels of padding

    black_pixels = []

    for y in range(height):
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            distance_squared = dx**2 + dy**2

            # Skip pixels outside the central circle
            if distance_squared > radius**2:
                continue

            r = Camera.imageGetRed(image, width, x, y)
            g = Camera.imageGetGreen(image, width, x, y)
            b = Camera.imageGetBlue(image, width, x, y)

            if r < 10 and g < 10 and b < 10:
                black_pixels.append((x, y))

    if not black_pixels:
        return None

    centroid_x = sum(x for x, y in black_pixels) / len(black_pixels)
    centroid_y = sum(y for x, y in black_pixels) / len(black_pixels)

    draw_centroid_marker(centroid_x, centroid_y, black_pixels)

    error_x = centroid_x - center_x
    error_y = centroid_y - center_y

    return error_x, error_y


def zoek_en_centreer_op_bol():
    k_p = 0.1
    max_speed = 0.05
    tolerance = 1

    vx_done = False
    vy_done = False
    
    while robot.step(TIME_STEP) != -1:
        kinematic.updateOdometry()
        pos = detect_black_position()

        if pos is None:
            print("⚠️ No black spot detected")
            mqtt_client.publish(f"robots/{robot_id}/panic", json.dumps({
                "robot_id": robot_id,
                "reason": "No black spot detected",
                "timestamp": datetime.utcnow().isoformat()
            }))
            break

        avg_x, avg_y = pos
        error_x = avg_x - 0.5
        error_y = avg_y - 0.5

        vx = vy = 0.0

        if not vx_done and abs(error_y) > tolerance:
            vx = -k_p * error_y
        else:
            vx_done = True

        if not vy_done and abs(error_x) > tolerance:
            vy = -k_p * error_x
        else:
            vy_done = True

        vx = max(min(vx, max_speed), -max_speed)
        vy = max(min(vy, max_speed), -max_speed)

        print(f"Centering step: vx={vx:.2f}, vy={vy:.2f}, error_x={error_x:.2f}, error_y={error_y:.2f}")

        if (vx_done and vy_done) or (vx == 0.0 and vy == 0.0):
            break

        set_wheel_speeds(vx, vy, 0.0, kinematic)

    for wheel in wheels:
        wheel.setVelocity(0.0)




def blijf_gwn_fcking_recht_rijden_stomme_physics(target_heading=goal_heading, k_p=2, max_omega=0.1, tolerance=0.05) -> float:
    while True:
        # compass_values = compass.getValues()
        # current_heading = math.atan2(compass_values[0], compass_values[2])
        current_heading = inertial_unit.getRollPitchYaw()[2]

        error = ((target_heading - current_heading + math.pi) % (2 * math.pi)) - math.pi
        omega = k_p * error
        omega = max(min(omega, max_omega), -max_omega)

        if abs(error) < tolerance:
            set_wheel_speeds(0.0, 0.0, omega, kinematic)
            break
        
        print(f"[Orientation Correction] Current Heading: {math.degrees(current_heading):.2f}°, Error: {math.degrees(error):.2f}°, Omega: {omega:.3f}")

        
        set_wheel_speeds(0.0, 0.0, omega, kinematic)
        robot.step(TIME_STEP)
    
    # print("Target heading reached. No more rotation.")

def rijdt(richting_rad, afstand):
    max_speed = 0.2
    min_speed = 0.02
    slow_down_radius = 0.4

    vx_base = math.cos(richting_rad)
    vy_base = math.sin(richting_rad)

    pos = kinematic.getPos()
    initial_pos = type(pos)(pos.x, pos.y, pos.theta)

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
            mqtt_client.publish(f"robots/{robot_id}/panic", json.dumps({
                "robot_id": robot_id,
                "reason": "Obstacle detected",
                "timestamp": datetime.utcnow().isoformat()
            }))
            return

        current_pos = kinematic.getPos()
        dx = current_pos.x - initial_pos.x
        dy = current_pos.y - initial_pos.y
        distance_travelled = math.sqrt(dx**2 + dy**2)
        remaining_distance = afstand - distance_travelled

        if remaining_distance <= tolerance:
            break

        # Ease out speed factor: linear drop-off
        speed_factor = min(1.0, remaining_distance / slow_down_radius)
        speed = min_speed + (max_speed - min_speed) * speed_factor

        vx = speed * vx_base
        vy = speed * vy_base

        set_wheel_speeds(vx, vy, 0.0, kinematic)

    for wheel in wheels:
        wheel.setVelocity(0.0)



# --- MQTT Client Logica ---
def on_connect(client, _1, _2, rc):
    print(f"Server connected with result code {rc}")
    client.subscribe(f"robots/{robot_id}/pickup")
    client.subscribe(f"robots/{robot_id}/drop_off")
    client.subscribe(f"robots/{robot_id}/move")
    client.subscribe("robots/panic")

def panic_loop():
    while robot.step(TIME_STEP) != -1:
        kinematic.updateOdometry()

def on_message(client, userdata, msg):
    payload_json = msg.payload.decode()
    topic = msg.topic
    print(f"robot {robot_id} got message from topic: {topic} -> {payload_json}")
    if topic == f"robots/{robot_id}/move":
        move_dict = from_json(payload_json)
        move = from_dict(MovementCommand, move_dict)
        task_queue.put(("move", move))
    elif topic == f"robots/{robot_id}/pickup":
        task_queue.put(("pickup", None))
    elif topic == f"robots/{robot_id}/drop_off":
        task_queue.put(("drop_off", None))
    elif topic == "robots/panic":
        panic_loop()




mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.loop_start() # loop start begint zelf al in een aparte thread
# threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()
# zoek_en_centreer_op_bol()
#test
# rijdt(math.pi, 4.0)
# rijdt(-math.pi/2, 1.0)

# --- Main Loop ---
while robot.step(TIME_STEP) != -1:
    kinematic.updateOdometry()
    blijf_gwn_fcking_recht_rijden_stomme_physics()
    kinematic.updateOdometry()
    if not task_queue.empty():
        task_type, data = task_queue.get()
        if task_type == "move":
            move = data
            startTime = robot.getTime()
            rijdt(math.radians(move.angle), move.distance)
            driving_time = robot.getTime() - startTime
            if move.correct_centering:
                zoek_en_centreer_op_bol()
            mqtt_client.publish("robots/move_arrive", json.dumps({
                "robot_id": robot_id,
                "success": True,
                "driving_time": driving_time
            }))
        elif task_type == "pickup":
            startTime = robot.getTime()
            pickup()
            picking_time = robot.getTime() - startTime
            mqtt_client.publish("robots/pickup", json.dumps({
                "robot_id": robot_id,
                "success": True,
                "picking_time": picking_time
            }))
        elif task_type == "drop_off":
            startTime = robot.getTime()
            drop_off()
            dropping_time = robot.getTime() - startTime
            mqtt_client.publish("robots/drop_off", json.dumps({
                "robot_id": robot_id,
                "success": True,
                "dropping_time": dropping_time
            }))

