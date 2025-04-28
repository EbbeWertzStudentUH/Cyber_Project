import json
import paho.mqtt.client as mqtt
from dataclasses import dataclass

@dataclass
class MovementCommand:
    x_dir: float
    y_dir: float
    degree: float
    speed: float

broker = "localhost"
port = 1883

def publish_movement_command(robot_id: str, command: MovementCommand):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    
    topic = f"robots/{robot_id}/move"
    payload = json.dumps(command.__dict__)
    
    client.publish(topic, payload)
    client.disconnect()

# Example: send a movement command to robot_1
cmd = MovementCommand(x_dir=69.0, y_dir=20.0, degree=0, speed=2.5)
publish_movement_command("robot_1", cmd)
