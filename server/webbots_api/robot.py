from datetime import datetime
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
robot_id = "robot_1"

def on_connect(client, userdata, flags, rc):
    print(f"Robot connected with result code {rc}")
    topic = f"robots/{robot_id}/move"
    client.subscribe(topic)
    print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    print(f"Received raw message: {msg.payload.decode()}")
    payload = json.loads(msg.payload.decode())
    command = MovementCommand(**payload)
    print(f"Received MovementCommand: {command}")

def send_panic(reason: str):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    
    panic = PanicSignal(robot_id=robot_id, reason=reason, timestamp=datetime.utcnow().isoformat())
    payload = json.dumps(panic.__dict__)
    
    topic = f"robots/{robot_id}/panic"
    client.publish(topic, payload)
    client.disconnect()

send_panic("Low battery detected!")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)
client.loop_forever()
