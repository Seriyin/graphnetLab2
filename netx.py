from collections import deque
from itertools import permutations, repeat, zip_longest
from random import choice
from typing import List, Tuple

import networkx as nx
from matplotlib import figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf


class Grapher:

    def __init__(self):
        self.graph = None
        self.round_known = None
        self.chosen = None
        self.term = None
        self.cumm = None

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

    def broadcast(self, percent: int) -> Tuple[List[int], bool]:
        self.round_known = [0]
        self.cumm = 0
        self.term = list(repeat(False, len(self.graph)))
        self.chosen = choice(range(0, len(self.graph)))
        self.term[self.chosen] = True
        next_neighbors = []
        index = round((len(self.graph[self.chosen]) * percent)/100.0)
        for x in self.graph[self.chosen]:
            if index != 0:
                self.graph.nodes[x]["q"].append((self.chosen, 1))
                next_neighbors.append(x)
                index -= 1
            else:
                break
        return self.start_round(1, next_neighbors, percent)

    def start_round(self, n: int, next_neighbors: List[int], percent: int) \
            -> Tuple[List[int], bool]:
        print(f"Starting round {n}, with {next_neighbors} and {percent}% diffusion")
        # Check queues are not empty (term)
        if sum([len(self.graph.nodes[i]['q']) for i in self.graph.nodes]) != 0:
            # Count for new round
            temp = []
            for x in next_neighbors:
                self.graph.nodes[x]['q'].clear()
                # Message has not reached neighbor before
                if not self.term[x]:
                    self.cumm += 1
                    self.term[x] = True
                    index = round((len(self.graph[x]) * percent) / 100.0)
                    for y in self.graph[x]:
                        if index != 0:
                            self.graph.nodes[y]['q'].append((x, n+1))
                            temp.append(y)
                            index -= 1
                        else:
                            break
            next_neighbors = temp
            self.round_known.append(self.cumm)
            return self.start_round(n+1, next_neighbors, percent)
        else:
            self.round_known.append(self.cumm)
            return self.round_known, all(self.term)

    def sample_graph_rounds(self, samples: int, size: int, percent: int) -> float:
        cumm = 0
        for _ in range(0, samples):
            self.generate_n(size)
            self.build_connected()
            sampleset, b = self.broadcast(percent)
            cumm += len(sampleset)-1
        return cumm/samples

    def sample_graphs(self, samples: int, size: int, percent: int) \
            -> Tuple[List[float], List[int], List[int]]:
        sampleset = []
        count = []
        term = []
        for _ in range(0, samples):
            self.generate_n(size)
            self.build_connected()
            p, b = self.broadcast(percent)
            sampleset = [x + y for x, y in zip_longest(sampleset, p, fillvalue=0)]
            temp = [x for x in repeat(1, len(p))]
            count = [x + y for x, y in zip_longest(temp, count, fillvalue=0)]
            if b:
                temp = list(repeat(0, len(count)))
                temp[len(p)-1] = 1
                term = [x + y for x, y in zip_longest(temp, term, fillvalue=0)]
        sampleset = [x / y for x, y in zip(sampleset, count)]
        cumm = [count[i] - x for i, x in enumerate(count[1:len(count)])]
        return sampleset, cumm, term


def main() -> None:
    graph = Grapher()
    samplemat = []
    for i in range(5, 100, 5):
        samplemat.append(graph.sample_graph_rounds(30, i, 100))
    f = figure.Figure(figsize=(12, 6))
    c = FigureCanvasPdf(f)
    ax = f.add_subplot(111)
    ax.set_xlabel("Number of nodes in graph")
    ax.set_ylabel("Average of rounds")
    ax.set_title("Rounds until full diffusion 30 graph samples")
    ax.plot(range(5, 100, 5), samplemat)
    f.savefig("roundgraphsampling.pdf", papertype='a4', dpi=200)
    f.clear()
    for j in range(100, 5, -5):
        samplemat, cumm, term = graph.sample_graphs(30, 100, j)
        ax = f.subplots(1, 3)
        f.suptitle(f"30 samples, 100 node graphs, {j}% neighbors chosen")
        ax[0].set_xlabel("Number of rounds")
        ax[0].set_ylabel("Average number of receipts")
        ax[0].plot(samplemat)
        ax[1].set_xlabel("Number of rounds")
        ax[1].set_ylabel("Terminations on round")
        ax[1].bar(range(len(cumm)), cumm, color="#6666ff")
        ax[2].set_xlabel("Number of rounds")
        ax[2].set_ylabel("No. Terminations, full diffusion")
        ax[2].bar(range(len(term)), term, color='#064930')
        f.savefig(f"roundgraphdiffusal{j}.pdf", papertype='a4', dpi=200)
        f.clear()


main()
