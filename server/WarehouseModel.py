from GraphModels import PathGraph, ShelveStop, QueueLine, Robot


class WarehouseModel:
    def __init__(self, graph:PathGraph, shelve_stops:list[ShelveStop], queue_line:QueueLine):
        self.graph = graph
        self.shelve_stops = shelve_stops
        self.queue_line = queue_line
        self.robots = dict[str, Robot]()

    def get_queue_size(self):
        return len(self.queue_line.queue_nodes)

    def set_new_robot(self, robot_id:str, queue_index:int):
        queue_node = self.queue_line.queue_nodes[queue_index]
        robot = Robot(robot_id, queue_node, None, False, False)
        self.robots[robot_id] = robot

class ModelSingleTon:
    def __init__(self):
        self.model = None
        self.svg_metadata = None
        self.original_svg = None
    def set_model(self, model: WarehouseModel):
        self.model = model
    def set_svg_metadata(self, svg_metadata: dict):
        self.svg_metadata = svg_metadata
    def set_original_svg(self, original_svg: bytes):
        self.original_svg = original_svg

MODEL_SINGLETON = ModelSingleTon()