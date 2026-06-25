'''
File that contains the definition of the ClothMesh class.
This class acts as a Data-Oriented container for all nodes and springs,
using NumPy arrays to allow for high-performance vectorized calculations.
'''
from dataclasses import dataclass
import numpy as np

@dataclass
class ClothMesh:
    '''
    A Data-Oriented representation of the cloth system.
    Instead of thousands of individual Node and Spring objects, 
    we store properties in continuous NumPy arrays.
    '''

    def __init__(self, num_nodes: int, num_springs: int):

        # NODE DATA
        # Shape: (num_nodes, 2). Column 0 is X, Column 1 is Y.
        self.pos = np.zeros((num_nodes, 2), dtype=np.float64)
        self.vel = np.zeros((num_nodes, 2), dtype=np.float64)
        self.force = np.zeros((num_nodes, 2), dtype=np.float64)

        # Shape: (num_nodes,) for scalar properties
        self.mass = np.ones(num_nodes, dtype=np.float64)
        self.fixed = np.zeros(num_nodes, dtype=bool)

        # SPRING DATA
        # Shape: (num_springs, 2). Stores the integer INDICES of connected nodes.
        # e.g., self.spring_indices[0] = [5, 6] means spring 0 connects node 5 and 6.
        self.spring_indices = np.zeros((num_springs, 2), dtype=np.int32)

        # Shape: (num_springs,) for rest lengths
        self.rest_lengths = np.zeros(num_springs, dtype=np.float64)
