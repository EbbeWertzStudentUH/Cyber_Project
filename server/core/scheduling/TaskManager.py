from core.model.graph_models import PathNode, PathEdge, ShelveStop, QueueNode
from core.model.RobotModel import ModelElement, Robot, ModelElementType
from core.model.WarehouseModel import WarehouseModel


class TaskManager:
    def __init__(self, model: WarehouseModel, path_planner):
        self.model = model
        self.path_planner = path_planner
        self.robot_paths = dict[str, list[ModelElement]]()

    def assign_fetch_task(self, robot: Robot, product_id: str):
        shelve_stop = next(s for s in self.model.shelve_stops if s.shelve_id == product_id)
        path_to_stop = self.path_planner.plan_path_from_queue(robot, shelve_stop)
        path_back_to_queue = self.path_planner.plan_path_to_queue(shelve_stop)
        full_path = path_to_stop + path_back_to_queue
        self.robot_paths[robot.id] = full_path
        self._advance(robot.id)

    def continue_robot_task(self, robot_id: str):
        robot = self.model.robots[robot_id]
        if robot_id not in self.robot_paths:
            return

        robot.current_element = robot.target_element
        robot.current_element_type = robot.target_element_type
        robot.target_element = None
        robot.target_element_type = None

        if isinstance(robot.current_element, QueueNode):
            robot.is_idle = True
            robot.has_package = False
            return

        self._advance(robot_id)

    def _advance(self, robot_id: str):
        robot = self.model.robots[robot_id]
        path = self.robot_paths[robot_id]
        if not path:
            return

        next_element = path.pop(0)
        robot.previous_element = robot.current_element
        robot.previous_element_type = robot.current_element_type
        robot.current_element_type = ModelElementType.DRIVABLE_EDGE  # assume motion
        robot.target_element = next_element
        robot.target_element_type = self._element_type(next_element)
        robot.is_idle = False

    @staticmethod
    def _element_type(element: ModelElement):
        if isinstance(element, PathNode):
            return ModelElementType.DRIVABLE_NODE
        elif isinstance(element, PathEdge):
            return ModelElementType.DRIVABLE_EDGE
        elif isinstance(element, ShelveStop):
            return ModelElementType.SHELVE_STOP
        elif isinstance(element, QueueNode):
            return ModelElementType.QUEUE_STOP