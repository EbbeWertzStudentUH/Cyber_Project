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
        print("chains: ")
        for cid, c in self.chains.items():
            print(f"{cid}: {[f"{nid}d{self.nx_graph.degree[nid]}" for nid in c]}")

    def _build_nx_graph(self):
        for node_id in self.graph.nodes:
            self.nx_graph.add_node(node_id)
        for (n1, n2) in self.graph.edges:
            self.nx_graph.add_edge(n1, n2)

    def _identify_chains(self):
        # Step 1: Get nodes with degree <= 2 (potential chain nodes)
        chain_nodes = {n for n in self.nx_graph.nodes if self.nx_graph.degree[n] <= 2}

        # Step 2: Build subgraph from just those nodes and their edges
        subgraph = self.nx_graph.subgraph(chain_nodes)

        # Step 3: Get connected components (these are your chains)
        for chain_id, component in enumerate(nx.connected_components(subgraph)):
            full_chain_nodes = set(component)

            # Step 4: Include any junctions directly connected to the component
            for node in component:
                for neighbor in self.nx_graph.neighbors(node):
                    if self.nx_graph.degree[neighbor] > 2:
                        full_chain_nodes.add(neighbor)

            self.chains[chain_id] = full_chain_nodes
            for node_id in full_chain_nodes:
                self.node_to_chain[node_id] = chain_id

    def get_chain_id(self, node_id: int):
        return self.node_to_chain.get(node_id, -1)

    def get_chain_nodes(self, chain_id: int):
        return self.chains.get(chain_id, set())
