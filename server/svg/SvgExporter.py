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

        for path_node in self.model.graph.nodes.values():
            circle_attrib = {
                'cx': str(path_node.x),
                'cy': str(path_node.y),
                'r': "0.2",
                'style': "fill:blue; stroke:none;"
            }
            ET.SubElement(new_root, 'circle', circle_attrib)

        # Step 2: Draw edges (lines) between the circles
        for path_edge in self.model.graph.edges.values():
            path_node1 = path_edge.node1
            path_node2 = path_edge.node2

            d = f"M {path_node1.x} {path_node1.y} L {path_node2.x} {path_node2.y}"

            path_attrib = {
                'd': d,
                'style': f"stroke:rgb({random.randint(0, 255)},{random.randint(0, 255)},{random.randint(0, 255)}); stroke-width:0.1; fill:none;"
            }
            ET.SubElement(new_root, 'path', path_attrib)

        tree = ET.ElementTree(new_root)
        tree.write(self.output_file, encoding="utf-8", xml_declaration=True)
