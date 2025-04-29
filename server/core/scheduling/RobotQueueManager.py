import math

from core.CoreSingleTon import CORE_SINGLETON
from core.model.RobotModel import Robot
from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import QueueNode, QueueLine
from webbots_api.command_types import MovementCommand


class QueueManager:
    def __init__(self, model: WarehouseModel):
        self.model = model

    def compact_queue(self):
        sorted_stops = sorted(self.model.queue_line.queue_nodes, key=lambda n: n.index)

        robots = list(self.model.robots.values())
        robots_on_stops = [r for r in robots if isinstance(r.current_element, QueueNode)]
        robots_on_queue_line = [r for r in robots if  isinstance(r.current_element, QueueLine)]
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
        start_coord = start_node.coordinate(self.model.queue_line)
        end_coord = target_node.coordinate(self.model.queue_line)

        CORE_SINGLETON.commander.calculate_and_command_move(robot.id, start_coord, end_coord)

        robot.goto_element_from_idle(self.model.queue_line, target_node)
