'''
Script that handles the core numerical integration for the cloth simulation.
Optimized with NumPy, Numba JIT, and NamedTuples for clean architecture.
'''
from collections import namedtuple
from numba import njit

# 1. Definiamo le strutture dati (NamedTuple) fuori dalle funzioni
# Funzionano come classi leggere, immutabili nella struttura ma velocissime
MeshContainer = namedtuple('MeshContainer', ['pos', 'vel', 'force', 'mass', 'fixed', 'spring_indices', 'rest_lengths'])
SimParams = namedtuple('SimParams', ['gravity', 'stiffness', 'damping', 'ground_y', 'dt'])


def step_physics(mesh, gravity, stiffness, damping, ground_y, dt=0.001, integration_method="velocity_verlet"):
    '''
    Executes a single physics simulation step.
    Impacchetta i dati del mesh e dell'ambiente in due comode NamedTuple prima del JIT.
    '''
    # Impacchettamento (Costo computazionale zero, sono solo puntatori)
    mesh_data = MeshContainer(
        pos=mesh.pos, vel=mesh.vel, force=mesh.force, mass=mesh.mass, 
        fixed=mesh.fixed, spring_indices=mesh.spring_indices, rest_lengths=mesh.rest_lengths
    )
    params = SimParams(
        gravity=gravity, stiffness=stiffness, damping=damping, ground_y=ground_y, dt=dt
    )

    # La chiamata ora è pulitissima!
    _step_physics_jit(mesh_data, params, integration_method)

    return _compute_energy(mesh_data, params)


@njit
def _step_physics_jit(mesh, params, integration_method):
    '''
    JIT-compiled core physics loop.
    '''
    if integration_method == "velocity_verlet":
        _velocity_verlet_method(mesh, params)
    elif integration_method == "symplectic_euler":
        _symplectic_euler_method(mesh, params)
    elif integration_method == "euler":
        _euler_method(mesh, params)



@njit
def _compute_forces(mesh, params):
    '''
    Calcola le forze basandosi sui dati impacchettati.
    '''
    num_nodes = len(mesh.mass)
    num_springs = len(mesh.rest_lengths)

    # 1. Reset forze e applicazione gravità + damping
    for i in range(num_nodes):
        mesh.force[i, 0] = -params.damping * mesh.vel[i, 0]
        mesh.force[i, 1] = params.gravity * mesh.mass[i] - params.damping * mesh.vel[i, 1]

    # 2. Forze elastiche delle molle
    for i in range(num_springs):
        p1_idx = mesh.spring_indices[i, 0]
        p2_idx = mesh.spring_indices[i, 1]

        dx = mesh.pos[p2_idx, 0] - mesh.pos[p1_idx, 0]
        dy = mesh.pos[p2_idx, 1] - mesh.pos[p1_idx, 1]

        current_dist = (dx**2 + dy**2)**0.5

        delta = current_dist - mesh.rest_lengths[i]
        force_scalar = params.stiffness * delta

        dir_x = dx / current_dist
        dir_y = dy / current_dist

        fx = force_scalar * dir_x
        fy = force_scalar * dir_y

        mesh.force[p1_idx, 0] += fx
        mesh.force[p1_idx, 1] += fy
        mesh.force[p2_idx, 0] -= fx
        mesh.force[p2_idx, 1] -= fy


@njit
def _euler_method(mesh, params):
    num_nodes = len(mesh.mass)

    _compute_forces(mesh, params)

    for i in range(num_nodes):
        if mesh.fixed[i]:
            continue

        mesh.pos[i, 0] += mesh.vel[i, 0] * params.dt
        mesh.pos[i, 1] += mesh.vel[i, 1] * params.dt

        mesh.vel[i, 0] += (mesh.force[i, 0] / mesh.mass[i]) * params.dt
        mesh.vel[i, 1] += (mesh.force[i, 1] / mesh.mass[i]) * params.dt

        if mesh.pos[i, 1] >= params.ground_y:
            mesh.pos[i, 1] = params.ground_y
            mesh.vel[i, 1] = 0.0
            mesh.vel[i, 0] = 0.0


@njit
def _symplectic_euler_method(mesh, params):
    num_nodes = len(mesh.mass)

    _compute_forces(mesh, params)

    for i in range(num_nodes):
        if mesh.fixed[i]:
            continue

        mesh.vel[i, 0] += (mesh.force[i, 0] / mesh.mass[i]) * params.dt
        mesh.vel[i, 1] += (mesh.force[i, 1] / mesh.mass[i]) * params.dt

        mesh.pos[i, 0] += mesh.vel[i, 0] * params.dt
        mesh.pos[i, 1] += mesh.vel[i, 1] * params.dt

        if mesh.pos[i, 1] >= params.ground_y:
            mesh.pos[i, 1] = params.ground_y
            mesh.vel[i, 1] = 0.0
            mesh.vel[i, 0] = 0.0


@njit
def _velocity_verlet_method(mesh, params):
    num_nodes = len(mesh.mass)
    dt_half = params.dt / 2.0

    # 1. Primo mezzo passo di velocità + aggiornamento posizioni
    for i in range(num_nodes):
        if mesh.fixed[i]:
            continue

        mesh.vel[i, 0] += (mesh.force[i, 0] / mesh.mass[i]) * dt_half
        mesh.vel[i, 1] += (mesh.force[i, 1] / mesh.mass[i]) * dt_half

        mesh.pos[i, 0] += mesh.vel[i, 0] * params.dt
        mesh.pos[i, 1] += mesh.vel[i, 1] * params.dt

        if mesh.pos[i, 1] >= params.ground_y:
            mesh.pos[i, 1] = params.ground_y
            mesh.vel[i, 1] = 0.0
            mesh.vel[i, 0] = 0.0

    # 2. Calcolo nuove forze basato sulle nuove posizioni
    _compute_forces(mesh, params)

    # 3. Secondo mezzo passo di velocità
    for i in range(num_nodes):
        if mesh.fixed[i]:
            continue

        mesh.vel[i, 0] += (mesh.force[i, 0] / mesh.mass[i]) * dt_half
        mesh.vel[i, 1] += (mesh.force[i, 1] / mesh.mass[i]) * dt_half

        if mesh.pos[i, 1] >= params.ground_y:
            mesh.vel[i, 1] = 0.0
            mesh.vel[i, 0] = 0.0

@njit
def _compute_energy(mesh, params):
    '''
    Calcola l'energia meccanica totale del sistema (Cinetica + Potenziale).
    L'unita di misura risultante e coerente con lo spazio dei pixel (kg * px^2 / s^2).
    '''
    num_nodes = len(mesh.mass)
    num_springs = len(mesh.rest_lengths)

    # 1. ENERGIA CINETICA (E_c = 0.5 * m * v^2)
    kinetic_energy = 0.0
    for i in range(num_nodes):
        # Velocità al quadrato: v_x^2 + v_y^2
        v_sq = mesh.vel[i, 0]**2 + mesh.vel[i, 1]**2
        kinetic_energy += 0.5 * mesh.mass[i] * v_sq

    # 2. ENERGIA POTENZIALE GRAVITAZIONALE (U_g = m * g * h)
    grav_energy = 0.0
    for i in range(num_nodes):
        # Poiché la Y cresce verso il basso, l'altezza rispetto al suolo invertita:
        height = params.ground_y - mesh.pos[i, 1]

        # Usiamo params.gravity (che è già in pixel/s^2)
        grav_energy += mesh.mass[i] * params.gravity * height

    # 3. ENERGIA POTENZIALE ELASTICA (U_e = 0.5 * k * delta^2)
    elastic_energy = 0.0
    for i in range(num_springs):
        p1_idx = mesh.spring_indices[i, 0]
        p2_idx = mesh.spring_indices[i, 1]

        # Distanza attuale tra i nodi della molla
        dx = mesh.pos[p2_idx, 0] - mesh.pos[p1_idx, 0]
        dy = mesh.pos[p2_idx, 1] - mesh.pos[p1_idx, 1]
        current_dist = (dx**2 + dy**2)**0.5

        # Deformazione (delta) rispetto alla lunghezza di riposo
        delta = current_dist - mesh.rest_lengths[i]

        # Energia della molla lineare (Legge di Hooke)
        elastic_energy += 0.5 * params.stiffness * (delta**2)

    return kinetic_energy + grav_energy + elastic_energy
