from core.model.RobotModel import ModelElementType
from core.model.WarehouseModel import WarehouseModel
from core.scheduling.PathPlanner import PathPlanner
from core.scheduling.QueueManager import QueueManager
from core.scheduling.TaskManager import TaskManager

class Scheduler:
    def __init__(self, model: WarehouseModel):
        self.model = model
        self.path_planner = PathPlanner(model)
        self.queue_manager = QueueManager(model)
        self.task_manager = TaskManager(model, self.path_planner)

    def handle_event(self, event_type: str, robot_id: str | None = None):
        self.queue_manager.compact_queue()

        if self.model.product_queue:
            idle_robots = [
                r for r in self.model.robots.values()
                if r.current_element_type == ModelElementType.QUEUE_STOP and r.is_idle
            ]
            if idle_robots:
                product_id = self.model.pop_product()
                self.task_manager.assign_fetch_task(idle_robots[0], product_id)

        if event_type == 'robot_arrival' and robot_id:
            self.task_manager.continue_robot_task(robot_id)
