import random
import xml.etree.ElementTree as ET
import networkx as nx

from GraphModels import PathNode
from svg.SvgModels import SvgMetaData


class ModelExporter:
    def __init__(self, graph: nx.Graph, output_file, svg_metadata: SvgMetaData):
        self.graph = graph
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

        for _, node in self.graph.nodes(data=True):
            path_node:PathNode = node['path_node']
            circle_attrib = {
                'cx': str(path_node.x),
                'cy': str(path_node.y),
                'r': "0.2",
                'style': "fill:blue; stroke:none;"
            }
            ET.SubElement(new_root, 'circle', circle_attrib)

        # Step 2: Draw edges (lines) between the circles
        for u, v, edge_data in self.graph.edges(data=True):
            path_node1: PathNode = self.graph.nodes[u]['path_node']
            path_node2 = self.graph.nodes[v]['path_node']

            d = f"M {path_node1.x} {path_node1.y} L {path_node2.x} {path_node2.y}"

            path_attrib = {
                'd': d,
                'style': f"stroke:rgb({random.randint(0, 255)},{random.randint(0, 255)},{random.randint(0, 255)}); stroke-width:0.1; fill:none;"
            }
            ET.SubElement(new_root, 'path', path_attrib)

        tree = ET.ElementTree(new_root)
        tree.write(self.output_file, encoding="utf-8", xml_declaration=True)
