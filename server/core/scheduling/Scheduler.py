from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import QueueNode
from core.scheduling.ChainPathManager import ChainPathManager
from core.scheduling.PathPlanner import PathPlanner
from core.scheduling.ReservationManager import ReservationManager
from core.scheduling.RobotQueueManager import QueueManager
from core.scheduling.TaskManager import TaskManager
from webbots_api.RobotCommander import RobotCommander
from webbots_api.command_types import PanicResponse, MoveArriveResponse, PickupResponse, DropOffResponse


class Scheduler:
    def __init__(self, model: WarehouseModel, commander:RobotCommander):
        self.model = model
        self.path_planner = PathPlanner(model)
        self.queue_manager = QueueManager(model, commander)
        self.task_manager = TaskManager(model, self.path_planner, commander)
        self.chain_manager = ChainPathManager(self.model.graph)
        self.reserver = ReservationManager(self.chain_manager)
        commander.on_panic = self.handle_panic
        commander.on_move_arrive = self.handle_move_arrive
        commander.on_pickup = self.handle_pickup
        commander.on_drop_off = self.handle_drop_off
        commander.on_any = self.update

    def update(self):
        self.queue_manager.update()
        idle_bots = [r for r in self.model.robots.values() if r.is_ready]
        if self.model.product_queue:
            waiting_robots = {r.current_element.index:r for r in idle_bots if isinstance(r.current_element, QueueNode)}
            if waiting_robots and 0 in waiting_robots:
                product_id = self.model.pop_product()
                self.task_manager.assign_fetch_goal(waiting_robots[0], product_id)

        for robot in idle_bots:
            task_node = self.task_manager.get_next_task(robot.id)
            if task_node and self.reserver.try_reserve(robot.id, task_node):
                self.task_manager.assign_next_task(robot.id, task_node)


    def handle_panic(self, panic: PanicResponse):
        pass

    def handle_move_arrive(self, arrive: MoveArriveResponse):
        robot = self.model.robots[arrive.robot_id]
        robot.target_arrive()
        self.reserver.release(arrive.robot_id)

    def handle_pickup(self, pickup: PickupResponse):
        robot = self.model.robots[pickup.robot_id]
        robot.is_ready = True
        robot.has_product = True

    def handle_drop_off(self, drop_off:DropOffResponse):
        robot = self.model.robots[drop_off.robot_id]
        robot.is_ready = True
        robot.has_product = False
