from core.model.RobotModel import ModelElement, Robot
from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import PathNode, ShelveStop, QueueNode
from webbots_api.RobotCommander import RobotCommander


class TaskManager:
    def __init__(self, model: WarehouseModel, path_planner, commander:RobotCommander):
        self.model = model
        self.path_planner = path_planner
        self.commander = commander
        self.robot_paths = dict[str, list[ModelElement]]()

    def assign_fetch_goal(self, robot: Robot, product_id: str):
        shelve_stop = next(s for s in self.model.shelve_stops if s.shelve_id == product_id)
        path_to_stop = self.path_planner.plan_path_from_queue(shelve_stop)
        path_back_to_queue = self.path_planner.plan_path_to_queue(shelve_stop)
        robot.product_id = product_id
        full_path = path_to_stop + path_back_to_queue
        print(full_path)
        self.robot_paths[robot.id] = full_path

    def get_next_task(self, robot_id: str):
        if robot_id not in self.robot_paths:
            return None

        path = self.robot_paths[robot_id]
        if not path:
            self.robot_paths.pop(robot_id)
            return None

        return path[0]  # Return without popping

    def assign_next_task(self, robot_id: str, task_element: ModelElement):
        robot = self.model.robots[robot_id]

        if not robot.is_ready:
            return
        if robot.current_element is None:
            return

        # Pickup logic: don't pop, just wait
        if isinstance(robot.current_element, ShelveStop) and not robot.has_product:
            self.commander.command_pickup(robot.id, robot.product_id)
            return

        # Now pop only if actually moving
        if robot_id in self.robot_paths and self.robot_paths[robot_id]:
            self.robot_paths[robot_id].pop(0)
            if not self.robot_paths[robot_id]:
                self.robot_paths.pop(robot_id)

        start_coord = self._node_coordinate(robot.current_element)
        end_coord = self._node_coordinate(task_element)
        center_correct = isinstance(task_element, PathNode)
        self.commander.calculate_and_command_move(robot_id, start_coord, end_coord, center_correct)
        robot.goto_element_from_ready(None, task_element)

    def _node_coordinate(self, target:ModelElement):
        if isinstance(target, PathNode):
            return target.x, target.y
        elif isinstance(target, ShelveStop):
            return target.coordinate()
        elif isinstance(target, QueueNode):
            return target.coordinate(self.model.queue_line)