import time

from core.model.WarehouseModel import WarehouseModel
from core.scheduling.Scheduler import Scheduler
from svg.SvgRenderer import SvgRenderer
from webbots_api.RobotCommander import RobotCommander


class CoreSingleTon:
    def __init__(self):
        self.model: WarehouseModel|None = None
        self.renderer: SvgRenderer|None = None
        self.commander = RobotCommander()
        self.scheduler: Scheduler|None = None
        self.simulated_robot_times = {}
    def set_model(self, model: WarehouseModel):
        self.model = model
        self.scheduler = Scheduler(model, self.commander)

    def update_view(self):

        # ================
        # SIMULATION: scheduled robots arrive 2 seconds after assignment
        # for robot in self.model.robots.values():
        #     if robot.is_ready:
        #         self.simulated_robot_times[robot.id] = time.time()
        #     elif time.time() - self.simulated_robot_times[robot.id] > 1:
        #         self.scheduler.register_robot_arrival(robot.id)
        #         self.simulated_robot_times[robot.id] = time.time()
        # self.scheduler.update()
        # ================

        self.renderer.update_model(self.model, self.scheduler.reserver.node_reservations.keys())

    def init_svg_renderer(self, original_svg: bytes):
        self.renderer = SvgRenderer(original_svg)


CORE_SINGLETON = CoreSingleTon()