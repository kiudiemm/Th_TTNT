"""
Bai 2: Tim duong di ngan nhat giua 2 dinh trong do thi bang A*
"""

import sys
from collections import deque

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class Graph:
    def __init__(self, adjac_lis):
        self.adjac_lis = adjac_lis
        # Dictionary luu toa do cac dinh (neu co) cho heuristic
        self.positions = {}

    def get_neighbors(self, v):
        return self.adjac_lis[v]

    # This is heuristic function which is having equal values for all nodes
    # Co the tuy chinh heuristic function tuy theo bai toan
    def h(self, n, goal=None):
        # Neu co goal, tinh Euclidean distance
        if goal and n in self.positions and goal in self.positions:
            x1, y1 = self.positions[n]
            x2, y2 = self.positions[goal]
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        # Neu khong co toa do, tra ve heuristic mac dinh (0)
        # Hoac co the dinh nghia heuristic tuy chinh
        H = {
            'A': 1,
            'B': 1,
            'C': 1,
            'D': 1,
            'E': 1,
            'F': 1,
            'G': 1,
            'H': 1,
            'I': 1,
            'X': 1,
            'Y': 1,
            'Z': 1,
            'W': 1
        }
        return H.get(n, 0)

    def set_position(self, vertex, x, y):
        """Thiet lap toa do cua dinh de tinh heuristic Euclidean"""
        self.positions[vertex] = (x, y)

    def a_star_algorithm(self, start, stop):
        # In this open_lst is a list of nodes which have been visited, but who's
        # neighbours haven't all been always inspected, It starts off with the start node
        # And closed_lst is a list of nodes which have been visited
        # and who's neighbors have been always inspected
        open_lst = set([start])
        closed_lst = set([])

        # poo has present distances from start to all other nodes
        # the default value is +infinity
        poo = {}
        poo[start] = 0

        # par contains an adjac mapping of all nodes
        par = {}
        par[start] = start

        while len(open_lst) > 0:
            n = None

            # it will find a node with the lowest value of f() -
            for v in open_lst:
                if n == None or poo[v] + self.h(v, stop) < poo[n] + self.h(n, stop):
                    n = v

            if n == None:
                print('Path does not exist!')
                return None

            # if the current node is the stop
            # then we start again from start
            if n == stop:
                reconst_path = []

                while par[n] != n:
                    reconst_path.append(n)
                    n = par[n]

                reconst_path.append(start)

                reconst_path.reverse()

                print('Path found: {}'.format(reconst_path))
                print('Total cost: {}'.format(poo[stop]))
                return reconst_path

            # for all the neighbors of the current node do
            for (m, weight) in self.get_neighbors(n):
                # if the current node is not presentin both open_lst and closed_lst
                # add it to open_lst and note n as it's par
                if m not in open_lst and m not in closed_lst:
                    open_lst.add(m)
                    par[m] = n
                    poo[m] = poo[n] + weight

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update par data and poo data
                # and if the node was in the closed_lst, move it to open_lst
                else:
                    if poo[m] > poo[n] + weight:
                        poo[m] = poo[n] + weight
                        par[m] = n

                        if m in closed_lst:
                            closed_lst.remove(m)
                            open_lst.add(m)

            # remove n from the open_lst, and add it to closed_lst
            # because all of his neighbors were inspected
            open_lst.remove(n)
            closed_lst.add(n)

        print('Path does not exist!')
        return None


# Main Code
if __name__ == "__main__":
    print("=" * 70)
    print("TEST 0: Test case tu anh")
    print("=" * 70)

    # Do thi tu anh
    adjac_lis = {
        'A': [('B', 1), ('C', 3), ('D', 7)],
        'B': [('D', 5)],
        'C': [('D', 12)],
        'D': []
    }

    graph1 = Graph(adjac_lis)

    start1 = 'A'
    stop1 = 'D'

    print("Tim duong di tu {} den {}".format(start1, stop1))
    path1 = graph1.a_star_algorithm(start1, stop1)
    print()

    print("=" * 70)
    print("TEST 1: Do thi don gian")
    print("=" * 70)

    # Tao do thi vi du
    adjac_lis = {
        'A': [('B', 1.0), ('C', 4.0)],
        'B': [('A', 1.0), ('C', 2.0), ('D', 5.0)],
        'C': [('A', 4.0), ('B', 2.0), ('D', 1.0), ('E', 3.0)],
        'D': [('B', 5.0), ('C', 1.0), ('E', 2.0), ('F', 4.0)],
        'E': [('C', 3.0), ('D', 2.0), ('F', 1.0)],
        'F': [('D', 4.0), ('E', 1.0)]
    }

    graph1 = Graph(adjac_lis)
    
    # Thiet lap toa do de tinh heuristic Euclidean
    graph1.set_position('A', 0, 0)
    graph1.set_position('B', 1, 1)
    graph1.set_position('C', 2, 0)
    graph1.set_position('D', 3, 2)
    graph1.set_position('E', 4, 1)
    graph1.set_position('F', 5, 2)

    start1 = 'A'
    stop1 = 'F'

    print("Tim duong di tu {} den {}".format(start1, stop1))
    path1 = graph1.a_star_algorithm(start1, stop1)

    print("\n" + "=" * 70)
    print("TEST 2: Do thi dang luoi")
    print("=" * 70)

    # Tao do thi dang luoi 3x3
    adjac_lis2 = {
        'A': [('B', 1.0), ('D', 1.0)],
        'B': [('A', 1.0), ('C', 1.0), ('E', 1.0)],
        'C': [('B', 1.0), ('F', 1.0)],
        'D': [('A', 1.0), ('E', 1.0), ('G', 1.0)],
        'E': [('B', 1.0), ('D', 1.0), ('F', 1.0), ('H', 1.0)],
        'F': [('C', 1.0), ('E', 1.0), ('I', 1.0)],
        'G': [('D', 1.0), ('H', 1.0)],
        'H': [('E', 1.0), ('G', 1.0), ('I', 1.0)],
        'I': [('F', 1.0), ('H', 1.0)]
    }

    graph2 = Graph(adjac_lis2)
    
    # Toa do luoi
    graph2.set_position('A', 0, 0)
    graph2.set_position('B', 1, 0)
    graph2.set_position('C', 2, 0)
    graph2.set_position('D', 0, 1)
    graph2.set_position('E', 1, 1)
    graph2.set_position('F', 2, 1)
    graph2.set_position('G', 0, 2)
    graph2.set_position('H', 1, 2)
    graph2.set_position('I', 2, 2)

    start2 = 'A'
    stop2 = 'I'

    print("Tim duong di tu {} den {} trong luoi 3x3".format(start2, stop2))
    path2 = graph2.a_star_algorithm(start2, stop2)

    print("\n" + "=" * 70)
    print("TEST 3: Truong hop khong co duong di")
    print("=" * 70)

    # Do thi khong ket noi
    adjac_lis3 = {
        'X': [('Y', 1.0)],
        'Y': [('X', 1.0)],
        'Z': [('W', 1.0)],
        'W': [('Z', 1.0)]
    }

    graph3 = Graph(adjac_lis3)

    start3 = 'X'
    stop3 = 'Z'

    print("Tim duong di tu {} den {} (khong co duong di)".format(start3, stop3))
    path3 = graph3.a_star_algorithm(start3, stop3)
