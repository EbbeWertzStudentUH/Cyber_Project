import math
from typing import List

from core.model.graph_models import PathNode, PathGraph, PathEdge, ShelveStop, QueueNode, QueueLine
from core.model.WarehouseModel import WarehouseModel
from svg.SvgExtractor import SVGExtractor
from svg.svg_models import SvgRgbMatch, SvgCircle, SvgLineSegment, SvgText, SvgRectangle


class SvgToModelBuilder:
    def __init__(self, svg_content: str, circle_radius=0.2):
        self.svg_content = svg_content
        self.circle_radius = circle_radius

        self.drivable_path_color = SvgRgbMatch(r=-80, g=-80, b=100)

        self.textbox_color = SvgRgbMatch(r=100, g=100, b=100)
        self.shelve_stop_color = SvgRgbMatch(r=100, g=100, b=-80)

        self.queue_line_color = SvgRgbMatch(r=100, g=-80, b=-80)
        self.queue_node_color = SvgRgbMatch(r=-80, g=100, b=-80)

        self.extractor = SVGExtractor(svg_content)
        self.graph = PathGraph()
        self.shelve_stops = []
        self.queue_line = None

        self.queue_enter_connected_node = None
        self.queue_leave_connected_node = None

    def build(self):
        self._build_graph()
        self._build_shelve_stops()
        self._build_queue_line()
        return WarehouseModel(self.graph, self.shelve_stops, self.queue_line)

    def _build_shelve_stops(self):
        """Builds ShelveStops from the yellow items and text boxes in the svg"""
        shelve_lines = self.extractor.extract_lines(self.shelve_stop_color)
        shelve_circles = self.extractor.extract_circles(self.shelve_stop_color)

        white_squares = self.extractor.extract_rectangles(self.textbox_color)
        text_boxes = self.extractor.extract_text_elements()

        for circle in shelve_circles:
            path_edge = self._get_intersecting_edge(circle, self.graph.edges.values())
            shelve_line = self._get_intersecting_line(circle, shelve_lines)
            text = self._get_textbox(shelve_line, text_boxes, white_squares)
            shelve_stop = ShelveStop.from_coordinates(circle.cx, circle.cy, path_edge, text.text)
            self.shelve_stops.append(shelve_stop)

    def _build_queue_line(self):
        """Builds the QueueLine model from the red line and red and green circles"""
        red_line = self.extractor.extract_lines(self.queue_line_color)[0]
        red_circle = self.extractor.extract_circles(self.queue_line_color)[0]
        green_circles = self.extractor.extract_circles(self.queue_node_color)

        # the start of line should be the red circle
        leave_x, leave_y = red_line.start

        line_end_x, line_end_y = red_line.end
        x1, y1 = red_circle.cx - self.circle_radius, red_circle.cy - self.circle_radius
        x2, y2 = red_circle.cx + self.circle_radius, red_circle.cy + self.circle_radius
        # if red is on the end, swap the start for end
        if self._coordinate_is_in_bounding_box(line_end_x, line_end_y, x1, y1, x2, y2):
            leave_x, leave_y = red_line.end

        node_disntances = [self._distance(leave_x, leave_y, c.cx, c.cy) for c in [red_circle] + green_circles]
        queue_nodes = [QueueNode(distance_from_leave=dist, index=i) for i, dist in enumerate(sorted(node_disntances))]
        enter_coordinate = (green_circles[0].cx, green_circles[0].cy)
        leave_coordinate = (red_circle.cx, red_circle.cy)
        self.queue_line = QueueLine(enter_coordinate, leave_coordinate, queue_nodes, self.queue_enter_connected_node, self.queue_leave_connected_node)

    def _build_graph(self):
        """Builds a PathGraph from the blue paths in the svg"""
        path_lines = self.extractor.extract_lines(self.drivable_path_color)
        path_circles = self.extractor.extract_circles(self.drivable_path_color)
        circle_to_node_id = dict[SvgCircle,int]()  # key:Circle -> value:node id
        red_circle = self.extractor.extract_circles(self.queue_line_color)[0]
        green_circles = self.extractor.extract_circles(self.queue_node_color)

        # add nodes
        for i, circle in enumerate(path_circles):
            path_node = PathNode(id=i, x=circle.cx, y=circle.cy)
            circle_to_node_id[circle] = i
            self.graph.add_node(i, path_node)

        # add edges
        for line in path_lines:
            intersecting_circles = self._get_intersecting_circles(line, path_circles)
            # sorting so that iteration always picks adjacent circle pairs
            intersecting_circles.sort(key=lambda c: (c.cx, c.cy))

            for i in range(len(intersecting_circles) - 1):
                node1_id = circle_to_node_id[intersecting_circles[i]]
                node2_id = circle_to_node_id[intersecting_circles[i + 1]]
                edge = PathEdge(self.graph.nodes[node1_id], self.graph.nodes[node2_id])
                self.graph.add_edge(node1_id, node2_id, edge)

            if len(intersecting_circles) == 1:
                if self._line_intersects_circle(line, red_circle):
                    self.queue_leave_connected_node = circle_to_node_id[intersecting_circles[0]]
                elif len(self._get_intersecting_circles(line, green_circles)) > 0:
                    self.queue_enter_connected_node = circle_to_node_id[intersecting_circles[0]]

    def _get_intersecting_circles(self, line: SvgLineSegment, circles: List[SvgCircle]) -> List[SvgCircle]:
        """Returns a list of Circle objects that intersect with the given LineSegment object."""
        intersecting_circles = []
        for circle in circles:
            if self._line_intersects_circle(line, circle):
                intersecting_circles.append(circle)
        return intersecting_circles

    def _get_intersecting_line(self, circle: SvgCircle, lines: List[SvgLineSegment]):
        for line in lines:
            if self._line_intersects_circle(line, circle):
                return line
        return None

    def _get_intersecting_edge(self, circle: SvgCircle, edges: list[PathEdge]):
        for edge in edges:
            node1, node2 = edge.node1, edge.node2
            x1, y1 = node1.x, node1.y
            x2, y2 = node2.x, node2.y
            if self._line_intersects_circle(SvgLineSegment((x1, y1), (x2, y2)), circle):
                return edge
        return None

    def _get_textbox(self, line: SvgLineSegment, texts:list[SvgText], textboxes:list[SvgRectangle]):
        for box in textboxes:
            if not self._line_ends_in_rectangle(line, box):
                continue
            for text in texts:
                bx1, by1, bx2, by2 = box.x, box.y, box.x + box.width, box.y + box.height
                if self._coordinate_is_in_bounding_box(text.x, text.y, bx1, by1, bx2, by2):
                    return text

    def _line_ends_in_rectangle(self, line: SvgLineSegment, rect: SvgRectangle):
        x1, y1 = line.start
        x2, y2 = line.end
        start_is_in = self._coordinate_is_in_bounding_box(x1, y1, rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        end_is_in = self._coordinate_is_in_bounding_box(x2, y2, rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        return start_is_in or end_is_in

    @staticmethod
    def _coordinate_is_in_bounding_box(x, y, box_x1, box_y1, box_x2, box_y2):
        horizontal = min(box_x1, box_x2) < x < max(box_x1, box_x2)
        vertical = min(box_y1, box_y2) < y < max(box_y1, box_y2)
        return horizontal and vertical

    def _line_intersects_circle(self, line: SvgLineSegment, circle: SvgCircle) -> bool:
        """Check if the line intersects with the given circle."""
        x1, y1 = line.start
        x2, y2 = line.end
        cx, cy = circle.cx, circle.cy

        # check if it is within the bounding box around the line segment
        if not (min(x1, x2) - self.circle_radius <= cx <= max(x1, x2) + self.circle_radius and
                min(y1, y2) - self.circle_radius <= cy <= max(y1, y2) + self.circle_radius):
            return False

        # chck if it is within perpendicular distance to the line (as infinite line)
        return self._perpendicular_distance_to_line(line, circle.cx, circle.cy) <= self.circle_radius

    @staticmethod
    def _perpendicular_distance_to_line(line: SvgLineSegment, x: float, y: float) -> float:
        """Return the shortest (perpendicular) distance from a point (x, y) to an infinite line defined by a line segment."""
        x1, y1 = line.start
        x2, y2 = line.end
        dx, dy = x2 - x1, y2 - y1
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / ((dx ** 2 + dy ** 2) ** 0.5)
        return d

    @staticmethod
    def _distance(x_start, y_start, x, y) -> float:
        return math.sqrt((x - x_start) ** 2 + (y - y_start) ** 2)