import math

import paho.mqtt.client as mqtt
from dacite import from_dict
from pydantic_core import from_json, to_json

from webbots_api.command_types import MovementCommand, PanicResponse, MoveArriveResponse, PickupResponse, \
    DropOffResponse, PickupCommand, DropOffCommand




class RobotCommander:
    def __init__(self, broker_url="localhost", broker_port=1883):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.on_panic = None
        self.on_move_arrive = None
        self.on_pickup = None
        self.on_drop_off = None
        self.on_any = None

    def connect(self):
        self.mqtt_client.connect(self.broker_url, self.broker_port, 60)
        self.mqtt_client.loop_start() # loop start runs in seperate thread unlike loop forever

    def disconnect(self):
        self.mqtt_client.disconnect()

    def command_move(self, robot_id: str, command: MovementCommand):
        topic = f"robots/{robot_id}/move"
        print(f"moving {robot_id}")
        payload = to_json(command)
        self.mqtt_client.publish(topic, payload)

    def command_pickup(self, robit_id:str, product_id:str):
        topic = f"robots/{robit_id}/pickup"
        payload = to_json(PickupCommand(product_id))
        self.mqtt_client.publish(topic, payload)

    def command_drop_off(self, robit_id:str, product_id:str):
        topic = f"robots/{robit_id}/drop_off"
        payload = to_json(DropOffCommand(product_id))
        self.mqtt_client.publish(topic, payload)

    def calculate_and_command_move(self, robot_id:str, start_coord:tuple[float, float], end_coord:tuple[float, float], correct:bool):
        start_x, start_y = start_coord
        end_x, end_y = end_coord
        dx, dy = end_x - start_x, end_y - start_y
        distance = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(-dy, dx)) % 360
        move_command = MovementCommand(distance=distance, angle=angle, correct_centering=correct)
        self.command_move(robot_id, move_command)

    @staticmethod
    def _on_connect(client, _1, _2, rc):
        print(f"Server connected with result code {rc}")
        client.subscribe("robots/panic")
        client.subscribe("robots/move_arrive")
        client.subscribe("robots/pickup")
        client.subscribe("robots/drop_off")

    def _on_message(self, client, userdata, msg):
        payload_dict = from_json(msg.payload.decode())
        topic = msg.topic
        match topic:
            case "robots/panic":
                panic = from_dict(PanicResponse, payload_dict)
                print(f"PANIC: {panic}")
                self.on_panic(panic)
            case "robots/move_arrive":
                arrive = from_dict(MoveArriveResponse, payload_dict)
                self.on_move_arrive(arrive)
            case "robots/pickup":
                pickup = from_dict(PickupResponse, payload_dict)
                self.on_pickup(pickup)
            case "robots/drop_off":
                drop_off = from_dict(DropOffResponse, payload_dict)
                self.on_drop_off(drop_off)
        self.on_any()