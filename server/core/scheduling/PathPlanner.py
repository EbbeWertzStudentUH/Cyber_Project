import networkx as nx

from core.model.graph_models import ShelveStop
from core.model.RobotModel import ModelElement
from core.model.WarehouseModel import WarehouseModel


class PathPlanner:
    def __init__(self, model: WarehouseModel):
        self.model = model
        self.nx_graph = nx.Graph()
        self._initialize_graph()

    def _initialize_graph(self):
        for node_id, node in self.model.graph.nodes.items():
            self.nx_graph.add_node(node_id, obj=node)
        for (n1, n2), edge in self.model.graph.edges.items():
            self.nx_graph.add_edge(n1, n2, weight=1.0, obj=edge)

    def plan_path_to_queue(self, from_element: ModelElement) -> list[ModelElement]:
        alternative_start_node = None
        if isinstance(from_element, ShelveStop):
            start_node = from_element.edge.node1
            alternative_start_node = from_element.edge.node2
        else:
            start_node = from_element

        end_node_id = self.model.queue_line.connected_enter_node_id
        path_node_ids = nx.shortest_path(self.nx_graph, source=start_node.id, target=end_node_id)
        if len(path_node_ids) > 1 and path_node_ids[1] == alternative_start_node.id:
            path_node_ids.pop(0)

        path_nodes = [self.model.graph.nodes[node_id] for node_id in path_node_ids]
        path_nodes.append(self.model.queue_line.queue_nodes[-1])  # append the QueueNode
        return path_nodes

    def plan_path_from_queue(self, shelve_stop: ShelveStop) -> list[ModelElement]:
        start_node_id = self.model.queue_line.connected_leave_node_id
        n1, n2 = shelve_stop.edge.node1.id, shelve_stop.edge.node2.id

        path = nx.shortest_path(self.nx_graph, source=start_node_id, target=n1, weight='weight')
        if len(path) > 1 and path[-2] == n2:
            path.pop() # if path ends in just n1, it is the shortest. If it ends in (n2, n1) the n1 can be skipped

        return [self.model.graph.nodes[node_id] for node_id in path] + [shelve_stop]

