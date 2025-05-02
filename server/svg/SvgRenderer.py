import copy
import math
import xml.etree.ElementTree as ET

from core.model.graph_models import PathNode, ShelveStop, QueueNode, QueueLine
from core.model.RobotModel import Robot, ModelElement
from core.model.WarehouseModel import WarehouseModel
from core.scheduling.ReservationManager import ReservationManager
from svg.SvgRobotView import SvgRobotView


class SvgRenderer:
    def __init__(self, base_svg_content):
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        self.original_tree = ET.ElementTree(ET.fromstring(base_svg_content))
        self.root = copy.deepcopy(self.original_tree.getroot())
        self.model:WarehouseModel|None = None
        self.reserved_node_ids = []

    def update_model(self, model:WarehouseModel, reserved_nodes):
        self.model = model
        self.reserved_node_ids = reserved_nodes

    def to_svg(self):
        self.root = copy.deepcopy(self.original_tree.getroot())
        if self.model:
            for robot in self.model.robots.values():
                self.draw_robot(robot)
            for path_node in self.model.graph.nodes.values():
                if path_node.id in self.reserved_node_ids:
                    self.create_circle(path_node.x, path_node.y, 'cyan', self.root)
                self.create_text(str(path_node.x), str(path_node.y), str(path_node.id), self.root)
        return ET.tostring(self.root, encoding="utf-8", xml_declaration=True).decode('utf-8')

    def draw_robot(self, robot: Robot):
        robot_id = robot.id
        has_package = robot.has_product
        is_idle = robot.is_ready

        x, y = 0.0, 0.0
        angle = 0.0

        if isinstance(robot.current_element, (PathNode, ShelveStop, QueueNode)):
            x, y = self.get_position_of_nodelike_element(robot.current_element)

        elif not robot.current_element or isinstance(robot.current_element, QueueLine):
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

        robot_view = SvgRobotView(robot_id, has_package, is_idle, angle, x, y)
        self.root.append(robot_view.to_element())

    def get_position_of_nodelike_element(self, element: ModelElement) -> tuple[float, float]:
        if isinstance(element, PathNode):
            return element.x, element.y
        elif isinstance(element, ShelveStop):
            return element.coordinate()
        elif isinstance(element, QueueNode):
            return element.coordinate(self.model.queue_line)
        else:
            raise TypeError(f"A node-like element was expected, not: {type(element)}")

    @staticmethod
    def create_circle(x, y, color, root):
        circle_attrib = {
            'cx': str(x),
            'cy': str(y),
            'r': "0.2",
            'style': f"fill:{color}; stroke:black; stroke-width:0.1"
        }
        ET.SubElement(root, 'circle', circle_attrib)

    @staticmethod
    def create_text(x, y, text, root):
        text_element = ET.SubElement(root, 'text', attrib={
            'x': x,
            'y': y,
            'fill': 'white',
            'font-size': '0.2',
            'text-anchor': 'middle',
            'dominant-baseline': 'middle',
        })
        text_element.text = text