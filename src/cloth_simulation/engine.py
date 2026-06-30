'''
Script that handles the core numerical integration for the cloth simulation using
a Semi-Implicit Euler (Symplectic Euler) integrator, optimized with NumPy and Numba JIT.
'''
from numba import njit


def step_physics(mesh, gravity, stiffness, damping, ground_y, dt=0.001):
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
        ground_y,
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
        ground_y,
        dt
    ):
    '''
    JIT-compiled core physics loop running at near-native C speed.
    '''

    num_nodes = len(mass)
    num_springs = len(rest_lengths)

    _symplectic_euler_method(
        num_nodes,
        num_springs,
        pos,
        vel,
        force,
        mass,
        fixed,
        ground_y,
        spring_indices,
        rest_lengths,
        gravity,
        stiffness,
        damping,
        dt
    )


@njit
def _compute_forces(
        num_nodes,
        num_springs,
        pos,
        vel,
        force,
        mass,
        spring_indices,
        rest_lengths,
        gravity,
        stiffness,
        damping,
    ):

    # 1. Reset forces, then apply gravitational force and damping
    for i in range(num_nodes):
        force[i, 0] = -damping * vel[i, 0]
        force[i, 1] = gravity * mass[i] - damping * vel[i, 1]

    # 2. Compute elastic forces
    for i in range(num_springs):
        p1_idx = spring_indices[i, 0]
        p2_idx = spring_indices[i, 1]

        dx = pos[p2_idx, 0] - pos[p1_idx, 0]
        dy = pos[p2_idx, 1] - pos[p1_idx, 1]

        current_dist = (dx**2 + dy**2)**0.5
        if current_dist == 0.0:
            continue

        delta = current_dist - rest_lengths[i]
        force_scalar = stiffness * delta

        dir_x = dx / current_dist
        dir_y = dy / current_dist

        fx = force_scalar * dir_x
        fy = force_scalar * dir_y

        force[p1_idx, 0] += fx
        force[p1_idx, 1] += fy
        force[p2_idx, 0] -= fx
        force[p2_idx, 1] -= fy


def _euler_method():
    pass


@njit
def _symplectic_euler_method(
        num_nodes,
        num_springs,
        pos,
        vel,
        force,
        mass,
        fixed,
        ground_y,
        spring_indices,
        rest_lengths,
        gravity,
        stiffness,
        damping,
        dt
    ):

    # 1. Calcola le forze basandoti sulle posizioni attuali
    _compute_forces(
        num_nodes,
        num_springs,
        pos,
        vel,
        force,
        mass,
        spring_indices,
        rest_lengths,
        gravity,
        stiffness,
        damping
    )

    # 2. Aggiorna velocità e posizioni per ogni nodo
    for i in range(num_nodes):
        if fixed[i]:
            continue

        # Simplettico: Aggiorna PRIMA la velocità usando le forze correnti
        vel[i, 0] += (force[i, 0] / mass[i]) * dt
        vel[i, 1] += (force[i, 1] / mass[i]) * dt

        # Simplettico: Aggiorna DOPO la posizione usando la NUOVA velocità
        pos[i, 0] += vel[i, 0] * dt
        pos[i, 1] += vel[i, 1] * dt

        # Gestione collisione con il terreno (Anelastic impact)
        if pos[i, 1] >= ground_y:
            pos[i, 1] = ground_y
            vel[i, 1] = 0.0
            vel[i, 0] = 0.0


def _velocity_verlet_method():
    pass

def _odeint_method():
    pass

def _yoshida_method():
    pass