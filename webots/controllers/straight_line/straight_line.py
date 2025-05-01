from dacite import from_dict
from controller import Robot, Camera
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

TIME_STEP = 32
robot = Robot()
kinematic = RobotKinematic.getInstance()
robot_id = robot.getName()
print(f"Controller started for robot {robot_id}")
broker = "localhost"
port = 1883

hasPackage = False

# Apparaten instellen
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

# Snelheden toepassen
def set_wheel_speeds(vx, vy, omega, kinematic):
    motion = kinematic.inversKinematic(vx, vy, omega)
    wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]
    for i in range(4):
        wheels[i].setVelocity(wheel_speeds[i])
        
def pickup():
    hasPackage = True
    wait_time = 2.0
    start_time = robot.getTime()
    while robot.getTime() - start_time < wait_time:
        kinematic.updateOdometry()
        set_wheel_speeds(0.0, 0.0, 0.0, kinematic)
    for i in range(4):
        wheels[i].setVelocity(0.0)

def drop_off():
    hasPackage = False
    wait_time = 2.0
    start_time = robot.getTime()
    while robot.getTime() - start_time < wait_time:
        kinematic.updateOdometry()
        set_wheel_speeds(0.0, 0.0, 0.0, kinematic)
    for i in range(4):
        wheels[i].setVelocity(0.0)

# Bol detecteren
def detect_white_position():
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()
    white_pixels = []

    for y in range(height):
        for x in range(width):
            if not (width * 0.15 <= x <= width * 0.85 and height * 0.15 <= y <= height * 0.85):
                continue

            r = Camera.imageGetRed(image, width, x, y)
            g = Camera.imageGetGreen(image, width, x, y)
            b = Camera.imageGetBlue(image, width, x, y)

            if r < 10 and g < 10 and b < 10:
                white_pixels.append((x, y))

    if not white_pixels:
        return None

    avg_x = sum(p[0] for p in white_pixels) / len(white_pixels)
    avg_y = sum(p[1] for p in white_pixels) / len(white_pixels)

    return avg_x / width, avg_y / height

def zoek_en_centreer_op_bol():
    while robot.step(TIME_STEP) != -1:
        kinematic.updateOdometry()
        pos = detect_white_position()
        if pos is None:
            mqtt_client.publish(f"robots/{robot_id}/panic", json.dumps({
                "robot_id": robot_id,
                "reason": "No white ball detected",
                "timestamp": datetime.utcnow().isoformat()
            }))
            break

        avg_x, avg_y = pos
        error_x = avg_x - 0.5
        error_y = avg_y - 0.5
        vx = vy = 0.0

        if abs(error_y) > 0.01:
            vx = -0.1 if error_y > 0 else 0.1
        if abs(error_x) > 0.01:
            vy = -0.1 if error_x > 0 else 0.1

        if abs(error_x) <= 0.05 and abs(error_y) <= 0.05:
            break

        set_wheel_speeds(vx, vy, 0.0, kinematic)

    for i in range(4):
        wheels[i].setVelocity(0.0)

def rijdt(richting_rad, afstand):
    snelheid = 0.2
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

        if distance_travelled >= afstand - tolerance:
            break

        set_wheel_speeds(vx, vy, omega, kinematic)

    for i in range(4):
        wheels[i].setVelocity(0.0)

# --- MQTT Client Logica ---
def on_connect(client, _1, _2, rc):
    print(f"Server connected with result code {rc}")
    client.subscribe(f"robots/{robot_id}/pickup")
    client.subscribe(f"robots/{robot_id}/drop_off")
    client.subscribe(f"robots/{robot_id}/move")
    client.subscribe("robots/panic")

def on_message(client, userdata, msg):
    payload_json = msg.payload.decode()
    topic = msg.topic
    print(f"robot {robot_id} got message from topic: {topic} -> {payload_json}")
    if topic == f"robots/{robot_id}/move":
        move_dict = from_json(payload_json)
        move = from_dict(MovementCommand, move_dict)
        startTime = robot.getTime()
        rijdt(math.radians(move.angle), move.distance)
        driving_time = robot.getTime() - startTime
        if move.correct_centering:
            zoek_en_centreer_op_bol()
        mqtt_client.publish(f"robots/move_arrive", json.dumps({
            "robot_id": robot_id,
            "success": True,
            "driving_time": driving_time,
        }))
    elif topic == f"robots/{robot_id}/pickup":            
        startTime = robot.getTime()
        pickup()
        picking_time = robot.getTime() - startTime
        mqtt_client.publish(f"robots/pickup", json.dumps({
            "robot_id": robot_id,
            "success": True,
            "picking_time": picking_time
        }))
    elif topic == f"robots/{robot_id}/drop_off":
        startTime = robot.getTime()
        drop_off()
        dropping_time = robot.getTime() - startTime
        mqtt_client.publish(f"robots/drop_off", json.dumps({
            "robot_id": robot_id,
            "success": True,
            "dropping_time": dropping_time
        }))

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker, port, 60)
mqtt_client.loop_start() # loop start begint zelf al in een aparte thread
# threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

#test
# rijdt(math.pi, 4.0)
# rijdt(-math.pi/2, 1.0)

# --- Main Loop ---
while robot.step(TIME_STEP) != -1:
    kinematic.updateOdometry()
    # De robot wacht op MQTT-opdrachten
