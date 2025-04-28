import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass

@dataclass
class MovementCommand:
    x_dir: float
    y_dir: float
    degree: float
    speed: float

@dataclass
class PanicSignal:
    robot_id: str
    reason: str
    timestamp: str

broker = "localhost"
port = 1883

def publish_movement_command(robot_id: str, command: MovementCommand):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    
    topic = f"robots/{robot_id}/move"
    payload = json.dumps(command.__dict__)
    
    client.publish(topic, payload)
    client.disconnect()

def on_connect(client, userdata, flags, rc):
    print(f"Server connected with result code {rc}")
    client.subscribe("robots/+/panic")

def on_message(client, userdata, msg):
    print(f"Panic message received on topic {msg.topic}")
    payload = json.loads(msg.payload.decode())
    panic = PanicSignal(**payload)
    print(f"PANIC ALERT from {panic.robot_id} at {panic.timestamp}: {panic.reason}")

# Example: send a movement command to robot_1
cmd = MovementCommand(x_dir=69.0, y_dir=20.0, degree=0, speed=2.5)
publish_movement_command("robot_1", cmd)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)
client.loop_forever()