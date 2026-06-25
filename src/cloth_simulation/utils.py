'''
Script that defines utility functions for generating a grid of nodes 
and springs for a cloth simulation using a Data-Oriented approach with NumPy.
'''
import math
from cloth_simulation.classes import ClothMesh


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
    Generates a grid layout and populates a ClothMesh instance.
    Calculates exact grid dimensions and pre-allocates flat NumPy arrays.
    Returns a populated ClothMesh instance.
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

    # 1. Compute the numeber of nodes and springs to be initialized
    num_nodes = nodes_x * nodes_y
    num_springs = (nodes_x - 1) * nodes_y + nodes_x * (nodes_y - 1)

    # 2. Initialize the ClothMesh container
    mesh = ClothMesh(num_nodes, num_springs)
    node_mass = mass / num_nodes

    spring_counter = 0

    # 3. Populate the matrix
    for row in range(nodes_y):
        for col in range(nodes_x):
            current_idx = row * nodes_x + col

            # Node data
            mesh.pos[current_idx, 0] = offset_x + col * dx  # X
            mesh.pos[current_idx, 1] = offset_y + row * dy  # Y
            mesh.mass[current_idx] = node_mass
            mesh.fixed[current_idx] = True if (row == 0 and col in fixed_indices) else False

            # Springs data
            # Connection with the node on the right
            if col < nodes_x - 1:
                right_idx = row * nodes_x + (col + 1)
                mesh.spring_indices[spring_counter] = [current_idx, right_idx]
                mesh.rest_lengths[spring_counter] = dx
                spring_counter += 1

            # Connection with the node below
            if row < nodes_y - 1:
                bottom_idx = (row + 1) * nodes_x + col
                mesh.spring_indices[spring_counter] = [current_idx, bottom_idx]
                mesh.rest_lengths[spring_counter] = dy
                spring_counter += 1

    return mesh
