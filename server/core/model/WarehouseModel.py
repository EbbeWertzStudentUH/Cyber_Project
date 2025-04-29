from core.model.GraphModels import PathGraph, ShelveStop, QueueLine
from core.model.RobotModel import Robot, ModelElementType


class WarehouseModel:
    def __init__(self, graph:PathGraph, shelve_stops:list[ShelveStop], queue_line:QueueLine):
        self.graph = graph
        self.shelve_stops = shelve_stops
        self.queue_line = queue_line
        self.robots = dict[str, Robot]()
        self.product_queue = list[str]() # product = shelve id

    def get_queue_size(self):
        return len(self.queue_line.queue_nodes)

    def set_new_robot(self, robot_id:str, queue_index:int):
        queue_node = self.queue_line.queue_nodes[queue_index]
        robot = Robot(robot_id, None, ModelElementType.QUEUE_STOP, None, None, queue_node, None, True, False)
        self.robots[robot_id] = robot

    def add_product_to_queue(self, item_shelve_id:str):
        self.product_queue.append(item_shelve_id)

    def pop_product(self) -> str:
        return self.product_queue.pop(0)

