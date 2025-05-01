from core.model.graph_models import PathGraph, ShelveStop, QueueLine
from core.model.RobotModel import Robot


class WarehouseModel:
    def __init__(self, graph:PathGraph, shelve_stops:list[ShelveStop], queue_line:QueueLine):
        self.graph = graph
        self.shelve_stops = shelve_stops
        self.queue_line = queue_line
        self.robots = dict[str, Robot]()
        self.product_queue = list[str]() # product = shelve id


    def get_ready_robots(self):
        return [r for r in self.robots.values() if r.is_ready]

    def get_queue_size(self):
        return len(self.queue_line.queue_nodes)

    def set_new_robot(self, robot_id:str, queue_index:int):
        queue_node = self.queue_line.queue_nodes[queue_index]
        robot = Robot(id=robot_id, current_element=queue_node)
        self.robots[robot_id] = robot

    def add_product_to_queue(self, item_shelve_id:str):
        self.product_queue.append(item_shelve_id)

    def pop_product(self) -> str:
        return self.product_queue.pop(0)

