"""
Bai 1: Giai bai toan 15 Puzzle bang thuat giai AKT (A*)
"""

import copy
import sys
from heapq import heappush, heappop

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Gia su puzzle(n=4) - 15 Puzzle
n = 4

# 4 vi tri dich chuyen tuong ung bottom, left, top, right
rows = [ 1, 0, -1, 0 ]
cols = [ 0, -1, 0, 1 ]

# Tao mot lop hang doi
class priorityQueue:
    def __init__(self):
        self.heap = []

    # Inserting a new key 'key'
    def push(self, key):
        heappush(self.heap, key)

    # funct to remove the element that is min from the Priority Queue
    def pop(self):
        return heappop(self.heap)

    # funct to check if the Queue is empty or not
    def empty(self):
        if not self.heap:
            return True
        else:
            return False

# structure of the node
class nodes:
    def __init__(self, parent, mats, empty_tile_posi,
                costs, levels):
        # This will store the parent node to the
        # current node And helps in tracing the
        # path when the solution is visible
        self.parent = parent

        # Useful for Storing the matrix
        self.mats = mats

        # useful for Storing the position where the
        # empty space tile is already existing in the matrix
        self.empty_tile_posi = empty_tile_posi

        # Store heuristic cost (Manhattan distance)
        self.costs = costs

        # Store no. of moves so far (g value)
        self.levels = levels

    # This func is used in order to form the
    # priority queue based on
    # f = g + h = levels + costs (A* algorithm)
    def __lt__(self, nxt):
        f_self = self.levels + self.costs
        f_nxt = nxt.levels + nxt.costs
        if f_self != f_nxt:
            return f_self < f_nxt
        return self.costs < nxt.costs

# method to calc. the Manhattan distance heuristic
# that is the sum of Manhattan distances of all tiles
# from their final positions
def calculateCosts(mats, final) -> int:
    distance = 0
    for i in range(n):
        for j in range(n):
            if mats[i][j] != 0:
                # Tim vi tri dich cua manh nay trong final state
                value = mats[i][j]
                target_row = (value - 1) // n
                target_col = (value - 1) % n
                distance += abs(i - target_row) + abs(j - target_col)
    return distance

def newNodes(mats, empty_tile_posi, new_empty_tile_posi,
            levels, parent, final) -> nodes:
    # Copying data from the parent matrixes to the present matrixes
    new_mats = copy.deepcopy(mats)

    # Moving the tile by 1 position
    x1 = empty_tile_posi[0]
    y1 = empty_tile_posi[1]
    x2 = new_empty_tile_posi[0]
    y2 = new_empty_tile_posi[1]
    new_mats[x1][y1], new_mats[x2][y2] = new_mats[x2][y2], new_mats[x1][y1]

    # Setting the heuristic cost (Manhattan distance)
    costs = calculateCosts(new_mats, final)

    new_nodes = nodes(parent, new_mats, new_empty_tile_posi,
                    costs, levels)
    return new_nodes

# func to print the N by N matrix
def printMatrix(mats):
    for i in range(n):
        for j in range(n):
            if mats[i][j] == 0:
                print(" . ", end=" ")
            else:
                print("%2d " % (mats[i][j]), end=" ")
        print()

# func to know if (x, y) is a valid or invalid
# matrix coordinates
def isSafe(x, y):
    return x >= 0 and x < n and y >= 0 and y < n

# Printing the path from the root node to the final node
def printPath(root):
    if root == None:
        return
    printPath(root.parent)
    printMatrix(root.mats)
    print()

# method for solving N*N - 1 puzzle algo
# by utilizing the A* algorithm. empty_tile_posi is
# the blank tile position initially.
def solve(initial, empty_tile_posi, final):
    # Creating a priority queue for storing the live
    # nodes of the search tree
    pq = priorityQueue()

    # Creating the root node
    costs = calculateCosts(initial, final)
    root = nodes(None, initial,
                empty_tile_posi, costs, 0)

    # Adding root to the list of live nodes
    pq.push(root)

    # Discovering a live node with min. costs,
    # and adding its children to the list of live
    # nodes and finally deleting it from
    # the list.
    visited = set()
    
    while not pq.empty():

        # Finding a live node with min. estimated
        # costs and deleting it form the list of the
        # live nodes
        minimum = pq.pop()
        
        # Convert matrix to tuple for set comparison
        mats_tuple = tuple(tuple(row) for row in minimum.mats)
        if mats_tuple in visited:
            continue
        visited.add(mats_tuple)

        # If the min. is ans node
        if minimum.costs == 0:
            # Printing the path from the root to
            # destination;
            printPath(minimum)
            print("So buoc: %d" % minimum.levels)
            print("So trang thai da duyet: %d" % len(visited))
            return

        # Generating all feasible children
        for i in range(4):
            new_tile_posi = [
                minimum.empty_tile_posi[0] + rows[i],
                minimum.empty_tile_posi[1] + cols[i], ]

            if isSafe(new_tile_posi[0], new_tile_posi[1]):

                # Creating a child node
                child = newNodes(minimum.mats,
                                minimum.empty_tile_posi,
                                new_tile_posi,
                                minimum.levels + 1,
                                minimum, final,)

                # Adding the child to the list of live nodes
                pq.push(child)

# Main Code

# Initial configuration
# Value 0 is taken here as an empty space
initial = [ [ 1, 2, 3, 4 ],
            [ 5, 6, 7, 8 ],
            [ 9, 10, 11, 12 ],
            [ 13, 14, 0, 15 ] ]

# Final configuration that can be solved
# Value 0 is taken as an empty space
final = [ [ 1, 2, 3, 4 ],
        [ 5, 6, 7, 8 ],
        [ 9, 10, 11, 12 ],
        [ 13, 14, 15, 0 ] ]

# Blank tile coordinates in the
# initial configuration
empty_tile_posi = [ 3, 2 ]

# Method call for solving the puzzle
print("=" * 50)
print("Giai bai toan 15 Puzzle bang thuat giai AKT (A*)")
print("=" * 50)
print("Trang thai ban dau:")
printMatrix(initial)
print("\nTrang thai dich:")
printMatrix(final)
print("\nCac buoc giai:")
solve(initial, empty_tile_posi, final)
