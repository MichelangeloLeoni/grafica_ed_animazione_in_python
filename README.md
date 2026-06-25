# Simulating cloth physics using Python and Tkinter

## Physics breakdown

We can approximate a cloth as a grid of particles connected by strings under the influnence of gravitiy and subjected to damping forces.

One could look at the problem as a discretization of a continuos elastic membrane, that satisfy the following partial differential equation:

$$\frac{\partial^2 \vec{u}}{\partial t^2} = c^2 \nabla^2 \vec{u}$$

where $\vec{u}$ is the displacement of the membrane and $c$ is the wave speed.

Starting from the Newton's second law of motion:

$$m\frac{d^2\vec{x}}{dt^2} = \vec{F}_{tot}$$

we get:

$$\frac{d \vec{v}}{dt} = \frac{\vec{F}_{tot}}{m}$$
$$\frac{d \vec{x}}{dt} = \vec{v}$$

This is the system of differential equations that we need to solve.

Thus, the total force acting on a particle is given by:

$$\vec{F}_{tot} = \vec{F}_{gravity} + \vec{F}_{damping} + \sum_{i=1}^{n} \vec{F}_{spring, \, i}$$

where $n$ is the number of springs connected to the particle.

### Gravitational force

The gravitational force acting on a particle is simply given by:

$$\vec{F}_{gravity} = m \cdot \vec{g}$$

where $m$ is the mass of the particle and $\vec{g}$ is the acceleration due to gravity.

In pseudocode, we can write:

```
def compute_gravity_force(mass, gravity):
    return mass * gravity
```

### Spring force

The spring force acting on a particle is given by Hooke's law:

$$\vec{F}_{spring} = -k \cdot (\vec{x} - \vec{x}_{rest})$$

where $k$ is the spring constant, $\vec{x}$ is the current position of the particle, and $\vec{x}_{rest}$ is the rest position of the spring.

In pseudocode, we can write:

```
def compute_spring_force(spring_constant, current_position, rest_position):
    return -spring_constant * (current_position - rest_position)
```

### Damping force

The damping force acting on a particle is given by:

$$\vec{F}_{damping} = -\gamma \cdot \vec{v}$$

where $\gamma$ is the damping coefficient and $\vec{v}$ is the velocity of the particle.

In pseudocode, we can write:

```
def compute_damping_force(damping_coefficient, velocity):
    return -damping_coefficient * velocity
```

## Solving the system of differential equations numerically

Using semi-implicit Euler method, we can update the velocity and position of each particle at each time step.

$$\vec{v}_{t+\Delta t} = \vec{v}_t + \frac{\vec{F}_{tot}}{m} \cdot \Delta t$$
$$\vec{x}_{t+\Delta t} = \vec{x}_t + \vec{v}_{t+\Delta t} \cdot \Delta t$$

PARLARE DELLA SCALETTA DI CALCOLO FORSE, ACCELERAZIONI, VELOCITÀ E POSIZIONI
PARLARE DELLA GESTIONE TEMPORALE E DEL LIMITE CHE LEGA TEMPO E MASSA DELLE PARTICELLE

