from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import QueueNode
from core.scheduling.PathPlanner import PathPlanner
from core.scheduling.RobotQueueManager import QueueManager
from core.scheduling.TaskManager import TaskManager
from webbots_api.RobotCommander import RobotCommander


class Scheduler:
    def __init__(self, model: WarehouseModel, commander:RobotCommander):
        self.model = model
        self.path_planner = PathPlanner(model)
        self.queue_manager = QueueManager(model, commander)
        self.task_manager = TaskManager(model, self.path_planner, commander)

    def update(self):
        self.queue_manager.compact_queue()
        idle_bots = [r for r in self.model.robots.values()if r.is_idle]
        if self.model.product_queue:
            waiting_robots = [r for r in idle_bots if isinstance(r.current_element_type, QueueNode)]
            if waiting_robots:
                product_id = self.model.pop_product()
                self.task_manager.assign_fetch_task(waiting_robots[0], product_id)

        for robot in idle_bots:
            self.task_manager.command_next_robot_task(robot.id)

    def register_robot_arrival(self, robot_id):
        self.model.robots[robot_id].target_arrive()
