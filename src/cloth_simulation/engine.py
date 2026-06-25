'''
Script that handles the core numerical integration for the cloth simulation using
a Semi-Implicit Euler (Symplectic Euler) integrator, optimized with NumPy and Numba JIT.
'''
from numba import njit


def step_physics(mesh, gravity, stiffness, damping, dt=0.001):
    '''
    Executes a single physics simulation step.
    Extracts raw NumPy arrays from the ClothMesh container and passes them
    to the lightning-fast JIT compiled execution loop.
    '''
    _step_physics_jit(
        mesh.pos,
        mesh.vel,
        mesh.force,
        mesh.mass,
        mesh.fixed,
        mesh.spring_indices,
        mesh.rest_lengths,
        gravity,
        stiffness,
        damping,
        dt
    )


@njit
def _step_physics_jit(
        pos,
        vel,
        force,
        mass,
        fixed,
        spring_indices,
        rest_lengths,
        gravity,
        stiffness,
        damping,
        dt
    ):
    '''
    JIT-compiled core physics loop running at near-native C speed.
    '''

    num_nodes = len(mass)
    num_springs = len(rest_lengths)

    # 1. Reset forces and apply gravitational force
    # force[:, 0] = X (0.0), force[:, 1] = Y (g * m)
    for i in range(num_nodes):
        force[i, 0] = 0.0
        force[i, 1] = gravity * mass[i]

    # 2. Accumulo delle forze elastiche interne (Legge di Hooke)
    for i in range(num_springs):
        p1_idx = spring_indices[i, 0]
        p2_idx = spring_indices[i, 1]

        # Calcolo della distanza (vettore e scalare)
        dx = pos[p2_idx, 0] - pos[p1_idx, 0]
        dy = pos[p2_idx, 1] - pos[p1_idx, 1]

        current_dist = (dx**2 + dy**2)**0.5
        if current_dist == 0.0:
            continue

        # F = k * (lunghezza_corrente - lunghezza_riposo)
        delta = current_dist - rest_lengths[i]
        force_scalar = stiffness * delta

        # Direzione del vettore forza
        dir_x = dx / current_dist
        dir_y = dy / current_dist

        fx = force_scalar * dir_x
        fy = force_scalar * dir_y

        # Terzo Principio di Newton (Azione e Reazione)
        force[p1_idx, 0] += fx
        force[p1_idx, 1] += fy
        force[p2_idx, 0] -= fx
        force[p2_idx, 1] -= fy

    # 3. Integrazione di Eulero Semi-Implicita
    for i in range(num_nodes):
        if fixed[i]:
            continue

        # Legge di Newton: a = F / m
        ax = force[i, 0] / mass[i]
        ay = force[i, 1] / mass[i]

        # Aggiornamento delle velocità con smorzamento (damping)
        vel[i, 0] += ax * dt
        vel[i, 1] += ay * dt
        vel[i, 0] *= (1.0 - damping)
        vel[i, 1] *= (1.0 - damping)

        # Aggiornamento della posizione usando la NUOVA velocità appena calcolata
        pos[i, 0] += vel[i, 0] * dt
        pos[i, 1] += vel[i, 1] * dt
