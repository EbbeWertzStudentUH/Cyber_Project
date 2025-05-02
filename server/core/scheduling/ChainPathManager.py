from core.model.graph_models import PathGraph


import networkx as nx

class ChainPathManager:
    def __init__(self, graph: PathGraph):
        self.graph = graph
        self.nx_graph = nx.Graph()
        self.node_to_chain = dict[int, int]() # node id -> chain id
        self.chains = dict[int, set[int]]() # chain id -> node ids
        self._build_nx_graph()
        self._identify_chains()

    def _build_nx_graph(self):
        for node_id in self.graph.nodes:
            self.nx_graph.add_node(node_id)
        for (n1, n2) in self.graph.edges:
            self.nx_graph.add_edge(n1, n2)

    def _identify_chains(self):
        visited = set()
        chain_id = 0

        for node_id in self.nx_graph.nodes:
            if node_id in visited or self.nx_graph.degree[node_id] > 2:
                continue

            path = []
            current = node_id
            prev = None

            while True:
                visited.add(current)
                path.append(current)
                neighbors = [n for n in self.nx_graph.neighbors(current) if n != prev]

                if len(neighbors) != 1:
                    break

                next_node = neighbors[0]
                if self.nx_graph.degree[next_node] > 2:
                    visited.add(next_node)
                    path.append(next_node)
                    break

                prev, current = current, next_node

            for n in path:
                self.node_to_chain[n] = chain_id
                self.chains[chain_id].add(n)
            chain_id += 1

    def get_chain_id(self, node_id: int):
        return self.node_to_chain.get(node_id, -1)

    def get_chain_nodes(self, chain_id: int):
        return self.chains.get(chain_id, set())
