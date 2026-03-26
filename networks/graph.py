import networkx as nx
from typing import List


def create_complete_graph(agent_ids: List[str]) -> nx.Graph:
    """Everyone sees everyone."""
    G = nx.complete_graph(len(agent_ids))
    mapping = {i: aid for i, aid in enumerate(agent_ids)}
    G = nx.relabel_nodes(G, mapping)
    return G


def create_small_world(agent_ids: List[str], k: int = 2, p: float = 0.3) -> nx.Graph:
    """Watts-Strogatz small world."""
    n = len(agent_ids)
    G = nx.watts_strogatz_graph(n, k, p)
    mapping = {i: aid for i, aid in enumerate(agent_ids)}
    G = nx.relabel_nodes(G, mapping)
    return G


def get_neighbors(G: nx.Graph, agent_id: str) -> List[str]:
    """Get the neighbor IDs for a given agent."""
    return list(G.neighbors(agent_id))
