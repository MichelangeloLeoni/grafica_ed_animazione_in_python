# Simulating cloth physics using Python and Tkinter

## Physics breakdown

We can approximate a cloth as a grid of particles connected by strings under the influnence of gravitiy and subjected to damping forces.

One could look at the problem as a discretization of a continuos elastic membrane, that satisfy the following partial differential equation:

$$\frac{\partial^2 \vec{u}}{\partial t^2} = c^2 \nabla^2 \vec{u}$$

where $\vec{u}$ is the displacement of the membrane and $c$ is the wave speed.

Starting from the Newton's second law of motion:

$$m\frac{d^2\vec{x}}{dt^2} = \vec{F}_{tot}$$

we get:

$$
\begin{cases}
\frac{d \vec{v}}{dt} = \frac{\vec{F}_{tot}}{m} \\
\frac{d \vec{x}}{dt} = \vec{v}
\end{cases}
$$

This is the system of differential equations that we need to solve.

Thus, the total force acting on a particle is given by:

$$\vec{F}_{tot} = \vec{F}_{gravity} + \vec{F}_{damping} + \sum_{i=1}^{n} \vec{F}_{spring, \, i}$$

where $n$ is the number of springs connected to the particle.

### Gravitational force

The gravitational force acting on a particle is simply given by:

$$\vec{F}_{gravity} = m \cdot \vec{g}$$

where $m$ is the mass of the particle and $\vec{g}$ is the acceleration due to gravity.

### Spring force

The spring force acting on a particle is given by Hooke's law:

$$\vec{F}_{spring} = -k \cdot (\vec{x} - \vec{x}_{rest})$$

where $k$ is the spring constant, $\vec{x}$ is the current position of the particle, and $\vec{x}_{rest}$ is the rest position of the spring.

### Damping force

The damping force acting on a particle is given by:

$$\vec{F}_{damping} = -\gamma \cdot \vec{v}$$

where $\gamma$ is the damping coefficient and $\vec{v}$ is the velocity of the particle.

## Solving the system of differential equations numerically

We can solve the system of ODEs using different integration methods:

- Symplectic Euler method:
    
    $$
    \vec v_{i+1} = \vec v_i + \vec a_i \cdot \Delta t\\
    \vec r_{i+1} = \vec r_i + \vec v_{i+1} \cdot \Delta t
    $$

    1. Compute forces
    2. Update velocity  
    3. Update position

    ```code
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
    ```
- Velocity Verlet:
    djfskd
    ```code
    test
    ```

PARLARE DELLA SCALETTA DI CALCOLO FORSE, ACCELERAZIONI, VELOCITÀ E POSIZIONI
PARLARE DELLA GESTIONE TEMPORALE E DEL LIMITE CHE LEGA TEMPO E MASSA DELLE PARTICELLE

## Code breakdown

### Generating the grid

# TODO:

- [ ] Add odeint method
- [ ] Add Yoshida method
- [ ] Clean up total energy visualization
- [ ] Clean and lint all the code
- [ ] Comment all the code
- [ ] Study theory