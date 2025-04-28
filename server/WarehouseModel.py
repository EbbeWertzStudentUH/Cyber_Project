from GraphModels import PathGraph, ShelveStop


class WarehouseModel:
    def __init__(self, graph:PathGraph, shelve_stops:list[ShelveStop]):
        self.graph =graph
        self.shelve_stops = shelve_stops

class ModelSingleTon:
    def __init__(self):
        self.model = None
        self.svg_metadata = None
    def set_model(self, model: WarehouseModel):
        self.model = model
    def set_svg_metadata(self, svg_metadata: dict):
        self.svg_metadata = svg_metadata

MODEL_SINGLETON = ModelSingleTon()