import json
import math
import paho.mqtt.client as mqtt
from dacite import from_dict

from webbots_api.command_types import MovementCommand, PanicResponse, MoveArriveResponse, PickupResponse, \
    DropOffResponse


def on_connect(client, _1, _2, rc):
    print(f"Server connected with result code {rc}")
    client.subscribe("robots/panic")
    client.subscribe("robots/move_arrive")
    client.subscribe("robots/pickup")
    client.subscribe("robots/drop_off")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    topic = msg.topic
    match topic:
        case "robots/panic":
            panic = from_dict(PanicResponse, payload)
            print(f"PANIC: {panic}")
        case "robots/move_arrive":
            arrive = from_dict(MoveArriveResponse, payload)

        case "robots/pickup_ok":
            pickup = from_dict(PickupResponse, payload)
        case "robots/drop_off_ok":
            drop_off = from_dict(DropOffResponse, payload)

class RobotCommander:
    def __init__(self, broker_url="localhost", broker_port=1883):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        self.broker_url = broker_url
        self.broker_port = broker_port

    def connect(self):
        self.mqtt_client.connect(self.broker_url, self.broker_port, 60)
        self.mqtt_client.loop_forever()

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