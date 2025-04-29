from dataclasses import dataclass
from enum import Enum, auto
from typing import Union
from core.model.graph_models import PathNode, PathEdge, ShelveStop, QueueLine, QueueNode

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

    def target_arrive(self):
        self._update_previous_element()
        self._update_current_element()
        self.target_element = None
        self.target_element_type = None
        self.is_idle = True

    def goto_element_from_idle(self, current_element: ModelElement, current_element_type: ModelElementType, target_element: ModelElement, target_element_type: ModelElementType):
        if self.target_element or not self.is_idle:
            raise RuntimeError("robot must be idle before being assigned a new movement task")
        self._update_previous_element()
        self.current_element = current_element
        self.current_element_type = current_element_type
        self.target_element = target_element
        self.target_element_type = target_element_type
        self.is_idle = False

    def _update_previous_element(self):
        self.previous_element = self.current_element
        self.previous_element_type = self.current_element_type

    def _update_current_element(self):
        self.current_element = self.target_element
        self.current_element_type = self.target_element_type