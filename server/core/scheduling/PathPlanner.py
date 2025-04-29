import networkx as nx

from core.model.graph_models import ShelveStop
from core.model.RobotModel import Robot, ModelElement
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

    def plan_path_from_queue(self, robot: Robot, shelve_stop: ShelveStop) -> list[ModelElement]:
        start_node_id = self.model.queue_line.connected_leave_node_id
        n1, n2 = shelve_stop.edge.node1.id, shelve_stop.edge.node2.id

        path1 = nx.shortest_path(self.nx_graph, source=start_node_id, target=n1, weight='weight')
        path2 = nx.shortest_path(self.nx_graph, source=start_node_id, target=n2, weight='weight')

        if len(path1) <= len(path2):
            path_nodes = path1
        else:
            path_nodes = path2

        result = []
        for i in range(len(path_nodes) - 1):
            edge = self.model.graph.edges[(path_nodes[i], path_nodes[i+1])]
            result.append(edge)
        result.append(shelve_stop)
        return result

    def plan_path_to_queue(self, from_element: ModelElement) -> list[ModelElement]:
        if isinstance(from_element, ShelveStop):
            start_node = from_element.edge.node1
        else:
            start_node = from_element

        end_node_id = self.model.queue_line.connected_enter_node_id
        path_nodes = nx.shortest_path(self.nx_graph, source=start_node.id, target=end_node_id)

        result = []
        for i in range(len(path_nodes) - 1):
            edge = self.model.graph.edges[(path_nodes[i], path_nodes[i+1])]
            result.append(edge)
        # Add queue stop
        last_stop = self.model.queue_line.queue_nodes[-1]
        result.append(last_stop)
        return result
