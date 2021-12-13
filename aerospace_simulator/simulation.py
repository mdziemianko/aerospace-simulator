from typing import Callable


class Simulation:
    def __init__(self):
        self.nodes = []

    def add(self, node):
        self.nodes.append(node)

    def tick(self, dt):
        # add topological sort
        for n in self.nodes:
            n.tick(dt)

    def finalise(self):
        for n in self.nodes:
            n.finalise()

    def simulate(self, is_end: Callable[[], bool], dt: float = 1):
        while not is_end():
            self.tick(dt)
        self.finalise()






