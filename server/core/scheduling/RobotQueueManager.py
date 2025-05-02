from core.model.RobotModel import Robot
from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import QueueNode, QueueLine
from webbots_api.RobotCommander import RobotCommander


class QueueManager:
    def __init__(self, model: WarehouseModel, commander:RobotCommander):
        self.model = model
        self.commander = commander

    def update(self):
        self.compact_queue()
        self.drop_off()

    def drop_off(self):
        robots = self.model.get_ready_robots()
        robots_on_stops = [r for r in robots if isinstance(r.current_element, QueueNode)]
        for r in robots_on_stops:
            if r.has_product:
                self.commander.command_drop_off(r.id, r.product_id)

    def compact_queue(self):
        sorted_stops = sorted(self.model.queue_line.queue_nodes, key=lambda n: n.index)

        robots = self.model.get_ready_robots()
        robots_on_stops = [r for r in robots if isinstance(r.current_element, QueueNode)]
        robots_on_queue_line = [r for r in robots if  isinstance(r.current_element, QueueLine)]

        current_occupied = {r.current_element.index: r for r in robots_on_stops}
        arriving_soon = {r.target_element.index for r in self.model.robots.values()
            if isinstance(r.target_element, QueueNode)}
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

        self.commander.calculate_and_command_move(robot.id, start_coord, end_coord, False)

        robot.goto_element_from_ready(self.model.queue_line, target_node)
