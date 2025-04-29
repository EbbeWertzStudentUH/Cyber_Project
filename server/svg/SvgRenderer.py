import copy
import math
import xml.etree.ElementTree as ET

from core.GraphModels import PathNode, ShelveStop, QueueNode
from core.RobotModel import Robot, ModelElementType, ModelElement
from core.WarehouseModel import WarehouseModel
from svg.SvgRobotView import SvgRobotView


class SvgRenderer:
    def __init__(self, base_svg_content):
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        self.original_tree = ET.ElementTree(ET.fromstring(base_svg_content))
        self.root = copy.deepcopy(self.original_tree.getroot())
        self.model:WarehouseModel|None = None

    def update_model(self, model:WarehouseModel):
        self.model = model

    def to_svg(self):
        self.root = copy.deepcopy(self.original_tree.getroot())
        if self.model:
            for robot in self.model.robots.values():
                self.draw_robot(robot)
        return ET.tostring(self.root, encoding="utf-8", xml_declaration=True).decode('utf-8')

    def draw_robot(self, robot: Robot):
        robot_id = robot.id
        has_package = robot.has_package
        is_idle = robot.is_idle

        x, y = 0.0, 0.0
        angle = 0.0

        if robot.current_element_type in [ModelElementType.DRIVABLE_NODE, ModelElementType.SHELVE_STOP,ModelElementType.QUEUE_STOP]:
            x, y = self.get_position_of_nodelike_element(robot.current_element)

        elif robot.current_element_type in [ModelElementType.DRIVABLE_EDGE, ModelElementType.QUEUE_LINE]:
            target_x, target_y = self.get_position_of_nodelike_element(robot.target_element)
            source_x, source_y = self.get_position_of_nodelike_element(robot.previous_element)

            dx = target_x - source_x
            dy = target_y - source_y

            length = math.hypot(dx, dy)
            if length == 0:
                dx, dy = 0, 0
            else:
                dx /= length
                dy /= length

            x = target_x - dx
            y = target_y - dy
            angle = math.degrees(math.atan2(dy, dx))

        else:
            raise ValueError(f"Unsupported robot current_element_type: {robot.current_element_type}")

        robot_view = SvgRobotView(robot_id, has_package, is_idle, angle, x, y)
        self.root.append(robot_view.to_element())

    def get_position_of_nodelike_element(self, element: ModelElement) -> tuple[float, float]:
        if isinstance(element, PathNode):
            return element.x, element.y
        elif isinstance(element, ShelveStop):
            return element.coordinate()
        elif isinstance(element, QueueNode):
            queue_line = self.model.queue_line
            leave_x, leave_y = queue_line.leave_coordinate
            enter_x, enter_y = queue_line.enter_coordinate
            dx = enter_x - leave_x
            dy = enter_y - leave_y
            total_length = (dx ** 2 + dy ** 2) ** 0.5
            fraction = element.distance_from_leave / total_length
            x = leave_x + dx * fraction
            y = leave_y + dy * fraction
            return x, y
        else:
            raise TypeError(f"A node-like element was expected, not: {type(element)}")
