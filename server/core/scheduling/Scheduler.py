from core.model.RobotModel import ModelElementType
from core.model.WarehouseModel import WarehouseModel
from core.scheduling.PathPlanner import PathPlanner
from core.scheduling.RobotQueueManager import QueueManager
from core.scheduling.TaskManager import TaskManager

class Scheduler:
    def __init__(self, model: WarehouseModel):
        self.model = model
        self.path_planner = PathPlanner(model)
        self.queue_manager = QueueManager(model)
        self.task_manager = TaskManager(model, self.path_planner)

    def update(self):
        self.queue_manager.compact_queue()
        idle_bots = [r for r in self.model.robots.values()if r.is_idle]
        if self.model.product_queue:
            waiting_robots = [r for r in idle_bots if r.current_element_type == ModelElementType.QUEUE_STOP]
            if waiting_robots:
                product_id = self.model.pop_product()
                self.task_manager.assign_fetch_task(waiting_robots[0], product_id)

        for robot in idle_bots:
            self.task_manager.continue_robot_task(robot.id)

    def register_robot_arrival(self, robot_id):
        self.model.robots[robot_id].target_arrive()
