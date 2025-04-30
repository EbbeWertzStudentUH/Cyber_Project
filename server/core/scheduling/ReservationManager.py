from core.model.graph_models import NodeLike


class ReservationManager:
    def __init__(self):
        self._robot_reservations = {}  # node_id -> robot_id
        self._node_reservations = {}  # robot_id -> node_id

    def try_reserve(self, robot_id: str, node: NodeLike) -> bool:
        if node in self._robot_reservations:
            return False
        self._robot_reservations[node] = robot_id
        self._node_reservations[robot_id] = node
        return True

    def release_if_moved_off(self, robot_id: str, node: NodeLike):
        reserved_node = self._node_reservations.get(robot_id)
        if reserved_node is not None and reserved_node != node:
            self._robot_reservations.pop(reserved_node, None)
            self._node_reservations.pop(robot_id, None)

    def is_reserved(self, node: NodeLike) -> bool:
        return node in self._robot_reservations
