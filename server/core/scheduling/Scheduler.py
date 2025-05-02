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
    def __init__(self, model: WarehouseModel, commander: RobotCommander):
        self.model = model
        self.path_planner = PathPlanner(model)
        self.queue_manager = QueueManager(model, commander)
        self.task_manager = TaskManager(model, self.path_planner, commander)
        self.chain_manager = ChainPathManager(self.model.graph)
        self.reserver = ReservationManager(self.chain_manager)

        commander.on_panic     = self.handle_panic
        commander.on_move_arrive = self.handle_move_arrive
        commander.on_pickup    = self.handle_pickup
        commander.on_drop_off  = self.handle_drop_off
        commander.on_any       = self.update

    def update(self):
        self.queue_manager.update()
        idle = [r for r in self.model.robots.values() if r.is_ready]

        # assign fetch tasks...
        if self.model.product_queue:
            qr = {r.current_element.index:r for r in idle if isinstance(r.current_element, QueueNode)}
            if qr and 0 in qr:
                pid = self.model.pop_product()
                self.task_manager.assign_fetch_goal(qr[0], pid)

        for robot in idle:
            task = self.task_manager.get_next_task(robot.id)
            if task is None:
                continue

            # path nodes need reservation
            if isinstance(task, PathNode):
                if self.reserver.try_reserve(robot.id, task.id):
                    self.task_manager.assign_next_task(robot.id, task)
                else:
                    # conflict → push resolution
                    self._attempt_push(robot, task)
            else:
                # queue or pickup/dropoff
                self.task_manager.assign_next_task(robot.id, task)

    def _attempt_push(self, robot: Robot, target: PathNode):
        blocker_id = self.reserver.get_reserving_robot(target.id)
        if not blocker_id or blocker_id == robot.id:
            return
        blocker = self.model.robots[blocker_id]

        # must be actually sitting on that node
        if not (isinstance(blocker.current_element, PathNode)
                and blocker.current_element.id == target.id):
            return

        # decide pusher vs passer
        r_chain = self.chain_manager.get_chain_id(robot.current_element.id)
        b_chain = self.chain_manager.get_chain_id(blocker.current_element.id)
        if   r_chain!=-1 and b_chain==-1:  pusher, passer = blocker, robot
        elif b_chain!=-1 and r_chain==-1:  pusher, passer = robot, blocker
        elif robot.has_product and not blocker.has_product:  pusher, passer = blocker, robot
        elif blocker.has_product and not robot.has_product:  pusher, passer = robot, blocker
        elif robot.id > blocker.id:       pusher, passer = robot, blocker
        else:                              pusher, passer = blocker, robot

        # find a push-aside node for the pusher
        curr = pusher.current_element.id
        neigh = self.model.graph.get_neighbors(curr)
        forbidden = {curr, target.id}
        if isinstance(passer.target_element, PathNode):
            forbidden.add(passer.target_element.id)

        options = [n for n in neigh if n not in forbidden]
        if not options:
            return

        # pick one and move
        push_to = min(options)
        if self.reserver.try_reserve(pusher.id, push_to):
            self.task_manager.assign_next_task(pusher.id,
                                               self.model.graph.nodes[push_to])
            print(f"🤖 PUSH: Robot {pusher.id} steps to {push_to} to free {passer.id}")
            # release old reservation so passer can grab it next tick
            self.reserver.release_chain_or_node(pusher.id, curr)

    def handle_move_arrive(self, resp: MoveArriveResponse):
        bot = self.model.robots[resp.robot_id]
        prev = bot.previous_element
        bot.target_arrive()
        # free old spot
        if isinstance(prev, PathNode):
            self.reserver.release_chain_or_node(bot.id, prev.id)

    def handle_pickup(self, p: PickupResponse):
        r = self.model.robots[p.robot_id]
        r.is_ready=True; r.has_product=True

    def handle_drop_off(self, d: DropOffResponse):
        r = self.model.robots[d.robot_id]
        r.is_ready=True; r.has_product=False

    def handle_panic(self, panic: PanicResponse):
        print("⚠️ Panic:", panic)
