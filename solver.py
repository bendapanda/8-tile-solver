# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 11:24:49 2023

@author: bensh
"""

from search import Frontier, Graph, Arc, generic_search, print_actions
from collections import deque
from itertools import dropwhile
import copy
import math
import heapq

class BranchCounter():
    """class to count states investigated as well as other stats"""
    def __init__(self):
        self.count = 0
        self.pruning = 0
    def add_count(self):
        self.count += 1
    def prune(self):
        self.pruning += 1
    
    def display_stats(self):
        print("states investigated: " + str(self.count))
        print("branches pruned: "+ str(self.pruning))

class DFSFrontier(Frontier):
    
    def __init__(self):
        self.stack = []
    
    def add(self, path):
        self.stack.append(path)
    def __next__(self):
        if len(self.stack) > 0:
            return self.stack.pop()        
        else:
            raise StopIteration
            
class BFSFrontier(Frontier):
    def __init__(self):
        self.container = deque()
    def add(self, path):
        self.container.append(path)
    def __next__(self):
        if len(self.container) > 0:
            return self.container.popleft()
        else:
            raise StopIteration

class LCFFrontier(Frontier):
    def __init__(self):
        self.container = []
        self.counter = 0
        self.pruning = True
        self.cache = set()
        
    def add(self, path, priority):
        self.counter += 1
        heapq.heappush(self.container, (priority, self.counter, path))
    def __next__(self):
        if len(self.container) > 0:
            return heapq.heappop(self.container)[-1]
        else:
            raise StopIteration
            
class AStarFrontier(Frontier):
    """frontier that combines the use of a heuristic, and lowest cost firts
    search.
    Implements a priority queue in which priority is dictated by the 
    cost of getting to the current position + the estimated numebr of moves left
    
    Includes the option for pruning"""
    def __init__(self, graph):
        self.container = []
        self.graph = graph
        self.counter = 0
        self.pruning = True
        self.cache = set()
    def add(self, path):
        if self.pruning and not path[-1] in self.cache:
            self.counter += 1
            path_cost = len(path)
            estimated_dist = self.graph.estimated_cost_to_goal(path[-1].head)
            priority = path_cost + estimated_dist
            heapq.heappush(self.container, (priority, self.counter, path))
    def __next__(self):
        while True:
            if len(self.container) > 0:
                path = heapq.heappop(self.container)
                if self.pruning:
                    if path not in self.cache:
                        self.cache.add(path)
                        return path[-1]
                else:
                    return path[-1]
            else:
                raise StopIteration
                    
        
class SlidingPuzzleGraph(Graph):
    def __init__(self, start_state):
        self.board_size = len(start_state)
        self.start_state = tuple_form(start_state)
        
        self.end_state = self.construct_end_state()
        
    
    def is_goal(self, node):
        """Returns true if the given node is a goal state, false otherwise."""
        return node == self.end_state
    def starting_nodes(self):
        """Returns a sequence of starting nodes. Often there is only one
        starting node but even then the function returns a sequence
        with one element. It can be implemented as an iterator if
        needed.

        """
        return (self.start_state, )
    
    def construct_end_state(self):
        """returns the end state for a board_size by board_size puzzle"""
        end_state = [[(self.board_size*i)+j for j in range(1,self.board_size+1)]\
                          for i in range(self.board_size)]
        end_state[-1][-1] = ' '
        print(end_state)
        return tuple_form(end_state)
        
    def outgoing_arcs(self, tail_node):
        """Given a node it returns a sequence of arcs (Arc objects)
        which correspond to the actions that can be taken in that
        state (node)."""
        arc_list = ();
        
        n = self.board_size
        blank_square_row, blank_square_column = self.get_tile_index(tail_node, ' ')
        state = list_form(tail_node)
        
        if blank_square_row < n-1:
            arc_list += (self.get_move_state(state, 'up', blank_square_row, blank_square_column,\
                                           blank_square_row+1, blank_square_column),)
        if blank_square_row > 0:
            arc_list += (self.get_move_state(state, 'down', blank_square_row, blank_square_column,\
                                           blank_square_row-1, blank_square_column),)
        if blank_square_column < n-1:
            arc_list += (self.get_move_state(state, 'left', blank_square_row, blank_square_column,\
                                           blank_square_row, blank_square_column+1),)
        if blank_square_column > 0:
            arc_list += (self.get_move_state(state, 'right', blank_square_row, blank_square_column,\
                                           blank_square_row, blank_square_column-1),)
        return arc_list
    
    def get_move_state(self, old_board, direction, old_row, old_column, new_row, new_column):
        """given a board and a move, returns an arc from the old state to a new one"""
        
        new_board = copy.deepcopy(old_board)
        new_board[old_row][old_column], new_board[new_row][new_column] = new_board[new_row][new_column], new_board[old_row][old_column]
        message = "Move " + str(new_board[old_row][old_column]) + ' ' + direction
        cost = 1
        return Arc(tuple_form(old_board), tuple_form(new_board), message, cost)
        
            
    
    def get_tile_index(self, state, tile):
        for row in range(self.board_size):
            for column in range(self.board_size):
                if state[row][column] == tile:
                    return row, column

    def estimated_cost_to_goal(self, node):
        """Return the estimated cost to a goal node from the given
        state. This function is usually implemented when there is a
        single goal state. The function is used as a heuristic in
        search. The implementation should make sure that the heuristic
        meets the required criteria for heuristics."""
        score = 0
        size = len(node)
        for i in range(size):
            for j in range(size):
                tile_value = node[i][j]
                if tile_value != ' ':
                    desired_x = (tile_value - 1) % size
                    desired_y = (tile_value - 1) // size
                    manhatten_dist = abs(desired_x - j) + abs(desired_y - i)
                    score += manhatten_dist
        return score

def tuple_form(board_state):
    """given an nxn board, returns a hashable format"""
    tuple_state = tuple()
    for row in board_state:
        tuple_state += (tuple(row), )
    return tuple_state

def list_form(board_state):
    """given an nxn board, returns it in list form"""
    return [[tile for tile in board_state[i]] for i in range(len(board_state))]

def main():
    graph = SlidingPuzzleGraph(((13, 4, 7, 6),
                                (8, 5, 9, 14),
                                (3, 11, 10, 15),
                                (2, 12, 1, ' ')))
    

    solutions = generic_search(graph, AStarFrontier(graph))
    print_actions(next(solutions))
if __name__ == "__main__":
    main()