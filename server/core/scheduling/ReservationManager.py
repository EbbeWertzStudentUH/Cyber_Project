from core.model.graph_models import NodeLike


class ReservationManager:
    def __init__(self):
        self._robot_reservations = {}  # node -> robot_id
        self._node_reservations = {}  # robot_id -> node

    def try_reserve(self, robot_id: str, node: NodeLike) -> bool:
        if node in self._robot_reservations:
            return False
        self._robot_reservations[node] = robot_id
        self._node_reservations[robot_id] = node
        return True

    def release(self, robot_id: str):
        reserved_node = self._node_reservations.get(robot_id)
        if reserved_node is not None:
            self._robot_reservations.pop(reserved_node)
            self._node_reservations.pop(robot_id)

    def is_reserved(self, node: NodeLike) -> bool:
        return node in self._robot_reservations
