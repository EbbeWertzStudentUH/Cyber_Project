from dataclasses import dataclass
from typing import Union
from core.model.graph_models import PathNode, ShelveStop, QueueLine, QueueNode

ModelElement = Union[PathNode,ShelveStop,QueueLine,QueueNode]

@dataclass
class Robot:
    id:str
    current_element: ModelElement
    previous_element: ModelElement | None = None
    target_element: ModelElement | None = None
    is_ready: bool = True
    has_product: bool = False
    product_id: str | None = None

    def target_arrive(self):
        self._update_previous_element()
        self._update_current_element()
        self.target_element = None
        self.is_ready = True

    def goto_element_from_ready(self, current_element: ModelElement, target_element: ModelElement):
        if self.target_element or not self.is_ready:
            raise RuntimeError("robot must be idle before being assigned a new movement task")
        self._update_previous_element()
        self.current_element = current_element
        self.target_element = target_element
        self.is_ready = False

    def _update_previous_element(self):
        self.previous_element = self.current_element

    def _update_current_element(self):
        self.current_element = self.target_element
