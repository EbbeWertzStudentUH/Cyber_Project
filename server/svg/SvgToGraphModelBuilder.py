import networkx as nx
from typing import List

from GraphModels import PathNode
from svg.SvgModels import SvgLineSegment, SvgCircle, SvgRgbMatch
from svg.SvgExtractor import SVGExtractor


class SvgToGraphModelBuilder:
    def __init__(self, svg_file: str, circle_radius=0.2, drivable_path_color=SvgRgbMatch(r=-80, g=-80, b=100)):
        self.svg_file = svg_file
        self.circle_radius = circle_radius
        self.drivable_path_color = drivable_path_color
        self.extractor = SVGExtractor(svg_file)
        self.graph = nx.Graph()  # NetworkX graph

    def build_graph(self) -> nx.Graph:
        """Builds a NetwokX graph from the blue paths in the svg"""
        # extract the blue elements
        blue_lines = self.extractor.extract_lines(self.drivable_path_color)
        blue_circles = self.extractor.extract_circles(self.drivable_path_color)

        circle_to_node_id = dict[SvgCircle,int]()  # key:Circle -> value:node id

        # add nodes
        for i, circle in enumerate(blue_circles):
            path_node = PathNode(id=i, x=circle.cx, y=circle.cy)
            circle_to_node_id[circle] = i
            self.graph.add_node(i, path_node=path_node)

        # add edges
        for line in blue_lines:
            intersecting_circles = self._get_intersecting_circles(line, blue_circles)
            # sorting so that iteration always picks adjacent circle pairs
            intersecting_circles.sort(key=lambda c: (c.cx, c.cy))

            for i in range(len(intersecting_circles) - 1):
                node1_id = circle_to_node_id[intersecting_circles[i]]
                node2_id = circle_to_node_id[intersecting_circles[i + 1]]
                self.graph.add_edge(node1_id, node2_id)

        return self.graph

    def _get_intersecting_circles(self, line: SvgLineSegment, circles: List[SvgCircle]) -> List[SvgCircle]:
        """Returns a list of Circle objects that intersect with the given LineSegment object."""
        intersecting_circles = []
        for circle in circles:
            if self._line_intersects_circle(line, circle):
                intersecting_circles.append(circle)
        return intersecting_circles

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
