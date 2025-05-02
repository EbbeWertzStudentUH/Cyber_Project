from core.scheduling.ChainPathManager import ChainPathManager


class ReservationManager:
    def __init__(self, chain_manager: ChainPathManager):
        self.chain_manager = chain_manager
        self.node_reservations = dict[int, str]()           # node_id -> robot_id
        self.robot_reserved_nodes = dict[str, set[int]]()   # robot_id -> set[node_id]

    def try_reserve(self, robot_id: str, node_id: int) -> bool:
        chain_id = self.chain_manager.get_chain_id(node_id)
        if chain_id is not None and chain_id >= 0:
            chain_nodes = self.chain_manager.get_chain_nodes(chain_id)
        else:
            chain_nodes = {node_id}  # Just the node itself

        # Check for reservation conflicts
        for nid in chain_nodes:
            reserved_by = self.node_reservations.get(nid)
            if reserved_by is not None and reserved_by != robot_id:
                return False

        # Reserve all nodes for this robot
        print(f"reserving {chain_nodes} for robot {robot_id}")
        for nid in chain_nodes:
            self.node_reservations[nid] = robot_id
            if robot_id not in self.robot_reserved_nodes:
                self.robot_reserved_nodes[robot_id] = set()
            self.robot_reserved_nodes[robot_id].add(nid)

        return True

    def release_chain_or_node(self, robot_id: str, node_id: int):
        chain_id = self.chain_manager.get_chain_id(node_id)
        if chain_id is not None and chain_id >= 0:
            release_nodes = self.chain_manager.get_chain_nodes(chain_id)
        else:
            release_nodes = {node_id}

        print(f"releasing {release_nodes} from robot {robot_id}")
        for nid in release_nodes:
            if self.node_reservations.get(nid) == robot_id:
                del self.node_reservations[nid]
                if robot_id in self.robot_reserved_nodes:
                    self.robot_reserved_nodes[robot_id].discard(nid)

        # Clean up if empty
        if robot_id in self.robot_reserved_nodes and not self.robot_reserved_nodes[robot_id]:
            del self.robot_reserved_nodes[robot_id]

    def release_all(self, robot_id: str):
        if robot_id not in self.robot_reserved_nodes:
            return
        for nid in self.robot_reserved_nodes[robot_id]:
            if self.node_reservations.get(nid) == robot_id:
                del self.node_reservations[nid]
        del self.robot_reserved_nodes[robot_id]

    def is_reserved(self, node_id: int) -> bool:
        return node_id in self.node_reservations

    def get_reserving_robot(self, node_id: int) -> str | None:
        return self.node_reservations.get(node_id)




