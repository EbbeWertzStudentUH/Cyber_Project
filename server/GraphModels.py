from dataclasses import dataclass

@dataclass
class PathNode:
    id: int
    x: float
    y: float

@dataclass
class PathEdge:
    node1: PathNode
    node2: PathNode

@dataclass
class PathGraph:
    nodes = dict[int, PathNode]()
    edges = dict[tuple[int, int], PathEdge]()

    def add_node(self, node_id: int, path_node: PathNode):
        self.nodes[node_id] = path_node

    def add_edge(self, node1_id: int, node2_id: int, path_edge: PathEdge):
        self.edges[(node1_id, node2_id)] = path_edge
        self.edges[(node2_id, node1_id)] = path_edge

@dataclass
class ShelveStop:
    pass