from core.model.WarehouseModel import WarehouseModel
from svg.SvgRenderer import SvgRenderer
from webbots_api.RobotCommander import RobotCommander


class CoreSingleTon:
    def __init__(self):
        self.model: WarehouseModel|None = None
        self.renderer: SvgRenderer|None = None
        self.commander = RobotCommander()
    def set_model(self, model: WarehouseModel):
        self.model = model
    def update_view(self):
        self.renderer.update_model(self.model)
    def init_svg_renderer(self, original_svg: bytes):
        self.renderer = SvgRenderer(original_svg)

CORE_SINGLETON = CoreSingleTon()