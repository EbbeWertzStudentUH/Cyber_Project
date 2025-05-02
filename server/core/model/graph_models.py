import math
from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class PathNode:
    id: int
    x: float
    y: float

    def __repr__(self): return f"path node {self.id}"

@dataclass(frozen=True)
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

    def get_neighbors(self, node_id: int) -> list[int]:
        return [n2 if n1 == node_id else n1
                for (n1, n2) in self.edges
                if node_id in (n1, n2)]


@dataclass(frozen=True)
class ShelveStop:
    edge: PathEdge
    shelve_id: str
    node_1_distance: float

    def coordinate(self):
        x1, y1 = self.edge.node1.x, self.edge.node1.y
        x2, y2 = self.edge.node2.x, self.edge.node2.y
        dx = x2 - x1
        dy = y2 - y1
        total_length = (dx ** 2 + dy ** 2) ** 0.5
        fraction = self.node_1_distance / total_length
        x = x1 + dx * fraction
        y = y1 + dy * fraction
        return x, y

    @classmethod
    def from_coordinates(cls, x:float, y:float, edge:PathEdge, shelve_id:str):
        x1, y1 = edge.node1.x, edge.node1.y
        dx = x1 - x
        dy = y1 - y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        return cls(edge=edge, shelve_id=shelve_id, node_1_distance=dist)

    def __repr__(self): return f"stop {self.shelve_id}"



@dataclass(frozen=True)
class QueueNode:
    index: int  # leave node = 0
    distance_from_leave: float

    def coordinate(self, line):
        leave_x, leave_y = line.leave_coordinate
        enter_x, enter_y = line.enter_coordinate
        dx = enter_x - leave_x
        dy = enter_y - leave_y
        total_length = (dx ** 2 + dy ** 2) ** 0.5
        fraction = self.distance_from_leave / total_length
        x = leave_x + dx * fraction
        y = leave_y + dy * fraction
        return x, y

    def __repr__(self): return f"queue node {self.index}"


@dataclass
class QueueLine:
    enter_coordinate: tuple[float, float]
    leave_coordinate: tuple[float, float]
    queue_nodes: list[QueueNode] # is sorted from leave to enter
    connected_enter_node_id: int
    connected_leave_node_id: int

    def __repr__(self): return "line"

NodeLike = Union[PathNode,ShelveStop,QueueNode]
