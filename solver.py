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
    def add(self, path, priority):
        self.counter += 1
        heapq.heappush(self.container, (priority, self.counter, path))
    def __next__(self):
        if len(self.container) > 0:
            return heapq.heappop(self.container)[-1]
        else:
            raise StopIteration
            

            
class FunkyNumericGraph(Graph):
    def __init__(self, start):
        self.start_node = start
        
    def is_goal(self, node):
        """Returns true if the given node is a goal state (div by 10
        ), false otherwise."""
        return node % 10 == 0

    def starting_nodes(self):
        """Returns a sequence of starting nodes. Often there is only one
        starting node but even then the function returns a sequence
        with one element. It can be implemented as an iterator if
        needed.
        """
        return (self.start_node, )

    def outgoing_arcs(self, tail_node):
        """Given a node it returns a sequence of arcs (Arc objects)
        which correspond to the actions that can be taken in that
        state (node)."""
        return (Arc(tail_node, tail_node-1, "1down", 1),\
                Arc(tail_node, tail_node+2, "2up", 1))

    def estimated_cost_to_goal(self, node):
        """Return the estimated cost to a goal node from the given
        state. This function is usually implemented when there is a
        single goal state. The function is used as a heuristic in
        search. The implementation should make sure that the heuristic
        meets the required criteria for heuristics."""

        raise NotImplementedError
        
class SlidingPuzzleGraph(Graph):
    def __init__(self, start_state):
        self.board_size = len(start_state)
        self.start_state = start_state
        
        self.end_state = self.construct_end_state()
        self.cache = set()
        
    
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
        end_state = [[(self.board_size*i)+j for j in range(1,self.board_size+1)]\
                          for i in range(self.board_size)]
        end_state[-1][-1] = ' '
        print(end_state)
        return end_state
    def get_priority(self, state):
        """returns a float showing how good the position is"""
        priority = 0
        for number in range(1, self.board_size):
            number_idealx = (number-1) % self.board_size
            number_idealy = (number-1) // self.board_size
            y, x = self.get_tile_index(state, number)
            x_score = 1 - abs(number_idealx - x) *  0.1
            y_score = 1 - abs(number_idealy - y) * 0.1
            priority += x_score
            priority += y_score

    def outgoing_arcs(self, tail_node):
        """Given a node it returns a sequence of arcs (Arc objects)
        which correspond to the actions that can be taken in that
        state (node)."""
        
        arc_list = ();
        hashable_form = tuple_form(tail_node)
        if hashable_form in self.cache: # if we have seen the state, return no options
            return arc_list
        
        self.cache.add(hashable_form)
        n = self.board_size
        blank_square_row, blank_square_column = self.get_tile_index(tail_node, ' ')
        
        if blank_square_row < n-1:
            arc_list += (self.get_move_state(tail_node, 'up', blank_square_row, blank_square_column,\
                                           blank_square_row+1, blank_square_column),)
        if blank_square_row > 0:
            arc_list += (self.get_move_state(tail_node, 'down', blank_square_row, blank_square_column,\
                                           blank_square_row-1, blank_square_column),)
        if blank_square_column < n-1:
            arc_list += (self.get_move_state(tail_node, 'left', blank_square_row, blank_square_column,\
                                           blank_square_row, blank_square_column+1),)
        if blank_square_column > 0:
            arc_list += (self.get_move_state(tail_node, 'right', blank_square_row, blank_square_column,\
                                           blank_square_row, blank_square_column-1),)
        return arc_list
    
    def get_move_state(self, old_board, direction, old_row, old_column, new_row, new_column):
        new_board = copy.deepcopy(old_board)
        new_board[old_row][old_column], new_board[new_row][new_column] = new_board[new_row][new_column], new_board[old_row][old_column]
        message = "Move " + str(new_board[old_row][old_column]) + ' ' + direction
        cost = 1
        return Arc(old_board, new_board, message, cost)
        
            
    
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

        raise NotImplementedError

def tuple_form(board_state):
    """given an nxn board, returns a hashable format"""
    tuple_state = tuple()
    for row in board_state:
        tuple_state += (tuple(row), )
    return tuple_state

def main():
    graph = SlidingPuzzleGraph([[8, 3, 4],
                                [1, 5, 6],
                                [7, 2, ' ']])

    solutions = generic_search(graph, LCFFrontier())
    print_actions(next(solutions))
if __name__ == "__main__":
    main()