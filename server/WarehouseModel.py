from GraphModels import PathGraph, ShelveStop, QueueLine


class WarehouseModel:
    def __init__(self, graph:PathGraph, shelve_stops:list[ShelveStop], queue_line:QueueLine):
        self.graph =graph
        self.shelve_stops = shelve_stops
        self.queue_line = queue_line

class ModelSingleTon:
    def __init__(self):
        self.model = None
        self.svg_metadata = None
        self.original_svg = None
    def set_model(self, model: WarehouseModel):
        self.model = model
    def set_svg_metadata(self, svg_metadata: dict):
        self.svg_metadata = svg_metadata
    def set_original_svg(self, original_svg: bytes):
        self.original_svg = original_svg

MODEL_SINGLETON = ModelSingleTon()