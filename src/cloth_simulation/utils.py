'''
Script that defines utility functions for generating a grid of nodes 
and springs for a cloth simulation. 
It calculates the appropriate number of nodes based on the specified width, height, 
and total number of nodes, and creates the necessary connections between nodes to form springs.
'''

import math
from proj.classes import Node, Spring


def generate_cloth_grid(
        width,
        height,
        mass,
        total_nodes,
        fixed_count,
        canvas_real_w, 
        canvas_real_h
    ):
    '''
    Generates a grid of nodes and springs for a cloth simulation.
    Calculates grid dimensions based on aspect ratio and total nodes.
    Returns a matrix of initialized nodes and a list of structural springs.
    '''

    aspect_ratio = width / height
    nodes_y = math.sqrt(total_nodes / aspect_ratio)
    nodes_x = total_nodes / nodes_y

    nodes_x = max(2, round(nodes_x))
    nodes_y = max(2, round(nodes_y))

    fixed_count = min(fixed_count, nodes_x)
    fixed_count = max(fixed_count, 1)

    fixed_indices = set()
    if fixed_count == 1:
        fixed_indices.add(nodes_x // 2)
    else:
        for i in range(fixed_count):
            idx = round(i * (nodes_x - 1) / (fixed_count - 1))
            fixed_indices.add(idx)

    dx = width / (nodes_x - 1)
    dy = height / (nodes_y - 1)

    offset_x = (canvas_real_w - width) / 2
    offset_y = (canvas_real_h - height) / 2

    # 1. Generate nodes
    node_mass = mass / (nodes_x * nodes_y)
    nodes_matrix = []
    for row in range(nodes_y):
        node_row = []
        for col in range(nodes_x):
            x = offset_x + col * dx
            y = offset_y + row * dy
            is_fixed = True if (row == 0 and col in fixed_indices) else False
            node_row.append(Node(x, y, mass=node_mass, fixed=is_fixed))
        nodes_matrix.append(node_row)

    # 2. Generate structural springs
    springs_list = []
    for row in range(nodes_y):
        for col in range(nodes_x):
            current_node = nodes_matrix[row][col]

            if col < nodes_x - 1:
                right_node = nodes_matrix[row][col + 1]
                springs_list.append(
                    Spring(current_node, right_node, "structural")
                )

            if row < nodes_y - 1:
                bottom_node = nodes_matrix[row + 1][col]
                springs_list.append(
                    Spring(current_node, bottom_node, "structural")
                )

    return nodes_matrix, springs_list
