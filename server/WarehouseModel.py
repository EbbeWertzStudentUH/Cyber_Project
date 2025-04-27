from GraphModels import PathGraph, ShelveStop


class WarehouseModel:
    def __init__(self, graph:PathGraph, shelve_stops:list[ShelveStop]):
        self.graph =graph
        self.shelve_stops = shelve_stops
