from core.model.RobotModel import Robot
from core.model.WarehouseModel import WarehouseModel
from core.model.graph_models import QueueNode, PathNode
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
            waiting_robots = {r.current_element.index: r for r in idle_bots if isinstance(r.current_element, QueueNode)}
            if waiting_robots and 0 in waiting_robots:
                product_id = self.model.pop_product()
                self.task_manager.assign_fetch_goal(waiting_robots[0], product_id)

        for robot in idle_bots:
            task_node = self.task_manager.get_next_task(robot.id)
            if task_node is None:
                continue

            if isinstance(task_node, PathNode):
                if self.reserver.try_reserve(robot.id, task_node.id):
                    self.task_manager.assign_next_task(robot.id, task_node)
                else:
                    # Do NOT pop the node. Wait and maybe resolve conflict.
                    self.resolve_conflict(robot, task_node)
            else:
                self.task_manager.assign_next_task(robot.id, task_node)

    def resolve_conflict(self, robot: Robot, target_node: PathNode) -> bool:
        blocking_robot_id = self.reserver.get_reserving_robot(target_node.id)
        if not blocking_robot_id or blocking_robot_id == robot.id:
            return False

        blocking_robot = self.model.robots[blocking_robot_id]

        # Node must be *currently* occupied to trigger dodge
        if not (isinstance(blocking_robot.current_element, PathNode) and
                blocking_robot.current_element.id == target_node.id):
            return False

        # Determine priority
        robot_chain = self.chain_manager.get_chain_id(robot.current_element.id)
        blocking_chain = self.chain_manager.get_chain_id(blocking_robot.current_element.id)

        dodge_robot = None
        passing_robot = None

        if robot_chain != -1 and blocking_chain == -1:
            dodge_robot, passing_robot = blocking_robot, robot
        elif blocking_chain != -1 and robot_chain == -1:
            dodge_robot, passing_robot = robot, blocking_robot
        elif robot.has_product and not blocking_robot.has_product:
            dodge_robot, passing_robot = blocking_robot, robot
        elif blocking_robot.has_product and not robot.has_product:
            dodge_robot, passing_robot = robot, blocking_robot
        elif robot.id > blocking_robot.id:
            dodge_robot, passing_robot = robot, blocking_robot
        else:
            dodge_robot, passing_robot = blocking_robot, robot

        # Don't dodge again if already dodging
        if (isinstance(dodge_robot.target_element, PathNode) and
                self.chain_manager.get_chain_id(dodge_robot.target_element.id) == -1 and
                self.chain_manager.get_chain_id(dodge_robot.current_element.id) == -1):
            return False

        # Find a safe junction neighbor to dodge into
        junction = target_node
        neighbors = self.model.graph.get_neighbors(junction.id)
        used = {robot.current_element.id, target_node.id}
        if isinstance(passing_robot.target_element, PathNode):
            used.add(passing_robot.target_element.id)

        safe_dodge_ids = [n for n in neighbors if n not in used]
        if not safe_dodge_ids:
            return False

        dodge_target_id = min(safe_dodge_ids)
        dodge_target = self.model.graph.nodes[dodge_target_id]

        if self.reserver.try_reserve(dodge_robot.id, dodge_target_id):
            self.task_manager.assign_next_task(dodge_robot.id, dodge_target)
            # Re-insert the conflict node back into task queue (so robot will go to it after dodge)
            self.task_manager.prepend_task(dodge_robot.id, target_node)
            print(f"🤖 Robot {dodge_robot.id} dodges to node {dodge_target_id} to let {passing_robot.id} pass.")
            return True

        return False

    @staticmethod
    def handle_panic(panic: PanicResponse):
        print(f"⚠️panic: {panic}")

    def handle_move_arrive(self, arrive: MoveArriveResponse):
        robot = self.model.robots[arrive.robot_id]
        to_release_node = robot.previous_element
        robot.target_arrive()
        if isinstance(to_release_node, PathNode):
            self.reserver.release_chain_or_node(robot.id, to_release_node.id)

    def handle_pickup(self, pickup: PickupResponse):
        robot = self.model.robots[pickup.robot_id]
        robot.is_ready = True
        robot.has_product = True

    def handle_drop_off(self, drop_off:DropOffResponse):
        robot = self.model.robots[drop_off.robot_id]
        robot.is_ready = True
        robot.has_product = False
