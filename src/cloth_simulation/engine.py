'''
Script that handles the core numerical integration for the cloth simulation using
a Semi-Implicit Euler (Symplectic Euler) integrator.
'''


def step_physics(
        nodes_matrix,
        springs_list,
        gravity,
        stiffness,
        damping,
        dt=0.04
    ):
    '''
    Executes a single physics simulation step.
    Applies gravity, accumulates spring forces, and updates node velocities
    and positions using Semi-Implicit Euler integration.
    '''

    # 1. Reset forces and apply gravity
    for row in nodes_matrix:
        for node in row:
            node.fx = 0.0
            node.fy = gravity * node.mass  # Weight force: F = m * g

    # 2. Accumulate internal elastic forces (Springs)
    for spring in springs_list:
        spring.apply_hookes_law(stiffness)

    # 3. Semi-Implicit Euler Integration
    for row in nodes_matrix:
        for node in row:
            if node.fixed:
                continue

            # Newton's Second Law: a = F / m
            ax = node.fx / node.mass
            ay = node.fy / node.mass

            # Update velocity first, applying the damping drag
            node.vx += (ax * dt)
            node.vy += (ay * dt)

            node.vx *= (1.0 - damping)
            node.vy *= (1.0 - damping)

            # Update position strictly using the NEW velocity
            node.x += node.vx * dt
            node.y += node.vy * dt
