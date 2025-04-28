from dataclasses import dataclass
from enum import Enum, auto
from typing import Union


class ModelElementType(Enum):
    DRIVABLE_NODE = auto()
    DRIVABLE_EDGE = auto()
    SHELVE_STOP = auto()
    QUEUE_LINE = auto()
    QUEUE_STOP = auto()

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
    edge: PathEdge
    shelve_id: str
    node_1_distance: float

    def coordinate(self):
        x = self.edge.node1.x + (self.edge.node2.x - self.edge.node1.x) * self.node_1_distance
        y = self.edge.node1.y + (self.edge.node2.y - self.edge.node1.y) * self.node_1_distance
        return x, y

    @classmethod
    def from_coordinates(cls, x:float, y:float, edge:PathEdge, shelve_id:str):
        x1, y1 = edge.node1.x, edge.node1.y
        x2, y2 = edge.node2.x, edge.node2.y

        length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
        t = ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / length_squared

        return cls(edge=edge, shelve_id=shelve_id, node_1_distance=t)

@dataclass
class QueueNode:
    index: int # leave node = 0
    distance_from_leave: float

@dataclass
class QueueLine:
    enter_coordinate: tuple[float, float]
    leave_coordinate: tuple[float, float]
    queue_nodes: list[QueueNode] # is sorted from leave to enter
    connected_enter_node_id: int
    connected_leave_node_id: int

ModelElement = Union[PathNode,PathEdge,ShelveStop,QueueLine,QueueNode]

@dataclass
class Robot:
    id:str
    previous_element_type: ModelElementType | None
    current_element_type: ModelElementType
    target_element_type: ModelElementType | None
    previous_element: ModelElement | None
    current_element: ModelElement
    target_element: ModelElement | None
    is_idle: bool
    has_package: bool