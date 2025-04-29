from core.model.GraphModels import QueueNode
from core.model.RobotModel import ModelElementType, Robot
from core.model.WarehouseModel import WarehouseModel


class QueueManager:
    def __init__(self, model: WarehouseModel):
        self.model = model

    def compact_queue(self):
        sorted_stops = sorted(self.model.queue_line.queue_nodes, key=lambda n: n.index)
        occupied = {
            r.current_element.index: r
            for r in self.model.robots.values()
            if r.current_element_type == ModelElementType.QUEUE_STOP
        }

        for node in sorted_stops:
            if node.index not in occupied:
                next_robot = self._next_robot_after(node.index, occupied)
                if next_robot:
                    self._move_to_spot(next_robot, node)
                break

    @staticmethod
    def _next_robot_after(index, occupied):
        for idx in sorted(occupied.keys()):
            if idx > index:
                return occupied[idx]
        return None

    @staticmethod
    def _move_to_spot(robot: Robot, target_node: QueueNode):
        robot.previous_element = robot.current_element
        robot.previous_element_type = robot.current_element_type
        robot.current_element_type = ModelElementType.QUEUE_LINE
        robot.target_element = target_node
        robot.target_element_type = ModelElementType.QUEUE_STOP
        robot.is_idle = False
