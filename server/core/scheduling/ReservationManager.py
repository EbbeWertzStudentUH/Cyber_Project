from core.model.graph_models import NodeLike, PathNode
from core.scheduling.ChainPathManager import ChainPathManager


class ReservationManager:
    def __init__(self, chain_manager: ChainPathManager):
        self.chain_manager = chain_manager
        self.node_reservations = dict[int, str]()  # node_id -> robot_id
        self.robot_reserved_nodes = dict[str, set[int]]()  # robot_id -> set[node_id]

    def try_reserve(self, robot_id: str, node: PathNode) -> bool:
        if node.id in self.node_reservations:
            return False

        chain_id = self.chain_manager.get_chain_id(node.id)
        if chain_id is not None:
            chain_nodes = self.chain_manager.get_chain_nodes(chain_id)
            for nid in chain_nodes:
                if nid in self.node_reservations and self.node_reservations[nid] != robot_id:
                    return False

        self.node_reservations[node.id] = robot_id
        self.robot_reserved_nodes[robot_id].add(node.id)
        return True

    def release(self, robot_id: str):
        for node_id in list(self.robot_reserved_nodes[robot_id]):
            if self.node_reservations.get(node_id) == robot_id:
                self.node_reservations.pop(node_id)
        self.robot_reserved_nodes[robot_id].clear()

    def is_reserved(self, node: PathNode) -> bool:
        return node.id in self.node_reservations

    def robot_owns(self, robot_id: str, node: PathNode) -> bool:
        return self.node_reservations.get(node.id) == robot_id

    def get_reserved_nodes(self, robot_id: str):
        return self.robot_reserved_nodes[robot_id]

