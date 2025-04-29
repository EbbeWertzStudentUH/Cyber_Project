from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
from core.model.GraphModels import PathNode, PathEdge, ShelveStop, QueueLine, QueueNode

ModelElement = Union[PathNode,PathEdge,ShelveStop,QueueLine,QueueNode]
class ModelElementType(Enum):
    DRIVABLE_NODE = auto()
    DRIVABLE_EDGE = auto()
    SHELVE_STOP = auto()
    QUEUE_LINE = auto()
    QUEUE_STOP = auto()

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
    product_id: str | None