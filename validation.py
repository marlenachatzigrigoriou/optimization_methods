import random
import math


class Solution:
    def __init__(self):
        self.routes = []
class Node:
    def __init__(self, id, tp, dem, xx, yy):
        self.id = id
        self.type = tp
        self.demand = dem
        self.x = xx
        self.y = yy
        if tp == 0:
            self.service_time = 0
        elif tp == 1:
            self.service_time = 5/60
        elif tp == 2:
            self.service_time = 15/60
        elif tp == 3:
            self.service_time = 25/60

class Route(object):
    def __init__(self, dp):
        self.capacity = 3000
        self.nodes = []
        self.nodes.append(dp)
        self.load = 0
        self.time = 0

    def calculate_time(self, dist_matrix):
        time = 0
        for i in range(1, len(self.nodes)):
            a = self.nodes[i-1]
            b = self.nodes[i]
            arc_time = dist_matrix[a.id][b.id] / 35
            time += arc_time
            time += b.service_time
        return time

all_nodes = []
service_locations = []
depot = Node(0, 0, 0, 50, 50)
all_nodes.append(depot)
random.seed(1)
for i in range(0, 200):
    id = i + 1
    tp = random.randint(1,3)
    dem = random.randint(1,5) * 100
    xx = random.randint(0, 100)
    yy = random.randint(0, 100)
    serv_node = Node(id, tp, dem, xx, yy)
    all_nodes.append(serv_node)
    service_locations.append(serv_node)

for i in range(0, len(all_nodes)):
    n = all_nodes[i]
    print(n.id, ',', n.x, ',', n.y, ',', n.type, ',', n.demand)
dist_matrix = [[0.0 for j in range(0, len(all_nodes))] for k in range(0, len(all_nodes))]
for i in range(0, len(all_nodes)):
    for j in range(0, len(all_nodes)):
        source = all_nodes[i]
        target = all_nodes[j]
        dx_2 = (source.x - target.x)**2
        dy_2 = (source.y - target.y) ** 2
        dist = round(math.sqrt(dx_2 + dy_2))
        dist_matrix[i][j] = dist
        print(str(dist), ',', end='')
    print()


def import_solution(all_nodes):
    sol = Solution()
    f = open("sol_8180070.txt", "r")
    line = 0
    for x in f:
        if line == 0:
            cost_reported = float(x)
            line += 1
        elif x[0] == '0':
            array_string = x.split(',')
            array_string[-1] = array_string[-1].split('\n')[0]
            rt = Route(all_nodes[0])
            rt.nodes = [all_nodes[int(str)] for str in array_string]
            sol.routes.append(rt)
    f.close()
    return cost_reported, sol

def check_validity_of_solution(cost_reported, sol):
    for i in range(1, len(all_nodes)):
        n = all_nodes[i]
        n.occurences = 0

    max_cost = -1
    for rt in sol.routes:
        rt_cost = 0
        rt_load = 0
        for i in range(0, len(rt.nodes) - 1):
            a = rt.nodes[i]
            b = rt.nodes[i+1]
            b.occurences += 1
            rt_load += b.demand
            rt_cost += ((dist_matrix[a.id][b.id] / 35) + b.service_time)

        if rt_cost > max_cost:
            max_cost = rt_cost
        if rt_load > rt.capacity:
            print('demand problem')

    if abs(max_cost - cost_reported) > 0.001:
        print('cost problem')

    for i in range(1, len(all_nodes)):
        n = all_nodes[i]
        if n.occurences != 1:
            print('problem with visits cust id', n.id)

    print('Validation OK', cost_reported)

cost_reported, s = import_solution(all_nodes)
check_validity_of_solution(cost_reported, s)

print(1)

