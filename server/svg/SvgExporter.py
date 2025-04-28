import random
import xml.etree.ElementTree as ET

from GraphModels import PathNode
from WarehouseModel import WarehouseModel
from svg.SvgModels import SvgMetaData


class ModelExporter:
    def __init__(self, model: WarehouseModel, output_file, svg_metadata: SvgMetaData):
        self.model = model
        self.output_file = output_file
        self.metadata = svg_metadata

    def create_new_svg(self):
        """Create a new SVG with randomized line colors and original circles."""
        svg_attrib = {
            'xmlns': "http://www.w3.org/2000/svg",
            'width': self.metadata.width,
            'height': self.metadata.height,
            'viewBox': self.metadata.viewBox,
        }

        new_root = ET.Element('svg', svg_attrib)

        for path_edge in self.model.graph.edges.values():
            path_node1 = path_edge.node1
            path_node2 = path_edge.node2
            self.create_line(path_node1.x, path_node1.y, path_node2.x, path_node2.y, 'blue', new_root)

        for path_node in self.model.graph.nodes.values():
            self.create_circle(path_node.x, path_node.y, 'cyan', new_root)

        for shelve_stop in self.model.shelve_stops:
            x, y = shelve_stop.coordinate()
            self.create_circle(x, y, 'yellow', new_root)


        tree = ET.ElementTree(new_root)
        tree.write(self.output_file, encoding="utf-8", xml_declaration=True)

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
    def create_line(x1, y1, x2, y2, color, root):
        d = f"M {x1} {y1} L {x2} {y2}"

        path_attrib = {
            'd': d,
            'style': f"stroke:{color}; stroke-width:0.1; fill:none;"
        }
        ET.SubElement(root, 'path', path_attrib)
