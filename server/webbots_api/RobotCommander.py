import json
import math

import paho.mqtt.client as mqtt
from webbots_api.command_types import MovementCommand, PanicSignal

def on_connect(client, _1, _2, rc):
    print(f"Server connected with result code {rc}")
    client.subscribe("robots/+/panic")

def on_message(_0, _1, msg):
    print(f"Panic message received on topic {msg.topic}")
    payload = json.loads(msg.payload.decode())
    panic = PanicSignal(**payload)
    print(f"PANIC ALERT from {panic.robot_id} at {panic.timestamp}: {panic.reason}")

class RobotCommander:
    def __init__(self, broker_url="localhost", broker_port=1883):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        # self.mqtt_client.connect(broker_url, broker_port, 60)
        # self.mqtt_client.loop_forever()

    def disconnect(self):
        self.mqtt_client.disconnect()

    def command_move(self, robot_id: str, command: MovementCommand):
        topic = f"robots/{robot_id}/move"
        payload = json.dumps(command.__dict__)
        self.mqtt_client.publish(topic, payload)

    def command_pickup(self, robit_id:str, product_id:str):
        topic = f"robots/{robit_id}/pickup"
        payload = json.dumps({"product_id": product_id})
        self.mqtt_client.publish(topic, payload)

    def command_drop_off(self, robit_id:str, product_id:str):
        topic = f"robots/{robit_id}/drop_off"
        payload = json.dumps({"product_id": product_id})
        self.mqtt_client.publish(topic, payload)

    def calculate_and_command_move(self, robot_id:str, start_coord:tuple[float, float], end_coord:tuple[float, float]):
        start_x, start_y = start_coord
        end_x, end_y = end_coord
        dx, dy = end_x - start_x, end_y - start_y
        distance = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx)) % 360
        move_command = MovementCommand(distance=distance, angle=angle)
        self.command_move(robot_id, move_command)