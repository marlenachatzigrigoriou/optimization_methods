import random
import math


class Model:

    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.capacity = -1

    def BuildModel(self):
        random.seed(1)
        depot = Node(0, 0, 0, 50, 50)
        self.allNodes.append(depot)
        self.capacity = 3000

        for i in range (0, 200):
            id = i + 1
            tp = random.randint(1, 3)
            dem = random.randint(1, 5) * 100
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            cust = Node(id, tp, dem, x, y)
            self.allNodes.append(cust)
            self.customers.append(cust)

        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                if (j==0) :
                    self.matrix[i][j] = 0.0
                else:
                    source = self.allNodes[i]
                    target = self.allNodes[j]
                    dx_2 = (source.x - target.x) ** 2
                    dy_2 = (source.y - target.y) ** 2
                    dist = round(math.sqrt(dx_2 + dy_2))
                    if self.allNodes[j].type == 1:
                        self.matrix[i][j] = (dist / 35) + 5.0 / 60.0
                    elif self.allNodes[j].type == 2:
                        self.matrix[i][j] = (dist / 35) + 15.0 / 60.0
                    elif self.allNodes[j].type == 3:
                        self.matrix[i][j] = (dist / 35) + 25.0 / 60.0


class Node:
    def __init__(self, idd, tp, dem, xx, yy):
        self.ID = idd
        self.type = tp
        self.demand = dem
        self.x = xx
        self.y = yy
        self.isRouted = False
        self.isTabuTillIterator = -1
        self.occurences = 0

class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.load = 0

    def __eq__(self, other): 
        if not isinstance(other, Route):
            return NotImplemented
        return self.sequenceOfNodes == other.sequenceOfNodes and self.cost == other.cost and self.capacity == other.capacity and self.load == other.load
