import math

from core.CoreSingleTon import CORE_SINGLETON
from core.model.RobotModel import ModelElementType, Robot
from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import QueueNode
from webbots_api.command_types import MovementCommand


class QueueManager:
    def __init__(self, model: WarehouseModel):
        self.model = model

    def compact_queue(self):
        sorted_stops = sorted(self.model.queue_line.queue_nodes, key=lambda n: n.index)

        robots = list(self.model.robots.values())
        robots_on_stops = [r for r in robots if r.current_element_type == ModelElementType.QUEUE_STOP]
        robots_on_queue_line = [r for r in robots if r.current_element_type == ModelElementType.QUEUE_LINE]
        for robot in robots_on_stops:
            assert robot.is_idle
        for robot in robots_on_queue_line:
            assert not (robot.is_idle or robot.target_element)

        current_occupied = {r.current_element.index: r for r in robots_on_stops}
        arriving_soon = {r.target_element.index for r in robots_on_queue_line}
        just_left = {r.previous_element.index for r in robots_on_queue_line
                     if isinstance(r.previous_element, QueueNode)}

        for node in sorted_stops:
            if (node.index in current_occupied or
                node.index in arriving_soon or
                node.index in just_left):
                continue

            next_robot = self._next_robot_after(node.index, current_occupied)
            if next_robot:
                self._update_robot(next_robot, node)
            break

    @staticmethod
    def _next_robot_after(index, occupied):
        for idx in sorted(occupied.keys()):
            if idx > index:
                return occupied[idx]
        return None

    def _update_robot(self, robot: Robot, target_node: QueueNode):
        start_node:QueueNode = robot.current_element
        start_x, start_y = self._get_queue_node_position(start_node)
        end_x, end_y = self._get_queue_node_position(target_node)

        dx, dy = end_x - start_x, end_y - start_y
        distance = math.hypot(dx, dy)
        angle = math.degrees(math.atan2(dy, dx)) % 360

        move_command = MovementCommand(distance=distance, angle=angle)
        CORE_SINGLETON.commander.command_move(robot.id, move_command)

        robot.goto_element_from_idle(self.model.queue_line, ModelElementType.QUEUE_LINE, target_node, ModelElementType.QUEUE_STOP)

    def _get_queue_node_position(self, node: QueueNode) -> tuple[float, float]:
        leave_x, leave_y = self.model.queue_line.leave_coordinate
        enter_x, enter_y = self.model.queue_line.enter_coordinate
        x = leave_x + (enter_x - leave_x) * node.distance_from_leave
        y = leave_y + (enter_y - leave_y) * node.distance_from_leave
        return x, y
