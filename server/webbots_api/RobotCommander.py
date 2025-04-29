import json
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
        self.mqtt_client.connect(broker_url, broker_port, 60)
        self.mqtt_client.loop_forever()

    def disconnect(self):
        self.mqtt_client.disconnect()

    def command_move(self, robot_id: str, command: MovementCommand):
        topic = f"robots/{robot_id}/move"
        payload = json.dumps(command.__dict__)
        self.mqtt_client.publish(topic, payload)