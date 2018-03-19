import networkx as nx
from random import choice
from itertools import permutations, repeat
from matplotlib import pyplot
from collections import deque


class Grapher:

    def __init__(self):
        self.graph = None
        self.round_known = None
        self.chosen = None
        self.term = None

    def generate_n(self, n: int) -> None:
        self.graph = nx.Graph()
        for x in range(0, n):
            self.graph.add_node(x, q=deque())
    
    def build_connected(self) -> None:
        prod = list(permutations(range(0, len(self.graph)),2))
        while not nx.is_connected(self.graph):
            (x, y) = choice(prod)
            prod.remove((x, y))
            self.graph.add_edge(x, y)

    def broadcast(self) -> None:
        self.round_known = [0]
        self.term = list(repeat(False,len(self.graph)))
        self.chosen = choice(range(0, len(self.graph)))
        self.term[self.chosen] = True
        next_neighbors = []
        for x in self.graph[self.chosen]:
            x["q"].append((self.chosen, 1))
            next_neighbors += x
        self.start_round(1, next_neighbors)

    def start_round(self, n: int, next_neighbors: list) -> None:
        print(f"Starting round {n}, with {next_neighbors}")
        # Check queues are not empty (term)
        if sum([i['q'] for i in self.graph.nodes]) == 0:
            # Count for new round
            self.round_known += 0
            temp = []
            for x in next_neighbors:
                x['q'].clear()
                # Message has not reached neighbor before
                if not self.term[x]:
                    self.round_known[n] += 1
                    self.term[x] = True
                    for y in self.graph[x]:
                        y['q'].append((x, n+1))
                        temp += y
            next_neighbors = temp
            self.start_round(n+1, next_neighbors)

    def sample_graphs(self, samples: int, size: int) -> float:
        sampleset = 0
        for _ in range(0,samples):
            self.generate_n(size)
            self.build_connected()
            sampleset += len(self.graph.edges)
        return sampleset/samples


def main() -> None:
    graph = Grapher()
    samplemat = []
    for i in range(5, 100, 5):
        samplemat.append(graph.sample_graphs(30, i))
    f = pyplot.figure()
    pyplot.xlabel("Number of nodes in graph")
    pyplot.ylabel("Median of edges from 30 graph samples")
    pyplot.title("Edges until graph is connected by node count")
    pyplot.plot(range(5, 100, 5), samplemat)
    pyplot.savefig('graphsampling.pdf')
    pyplot.close(f)


main()
