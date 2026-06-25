'''
Core application script containing the ClothApp class which manages the application state,
shortcuts, and orchestrates the rendering and physics loops.
'''
import time
import tkinter as tk
import numpy as np
from cloth_simulation.canvas import ClothCanvas
from cloth_simulation.ui_panels import ControlPanel
import cloth_simulation.engine as phys
import cloth_simulation.utils as gf

DEFAULTS = {
    'width': 400,
    'height': 400,
    'mass': 100.0,
    'total_nodes': 500,
    'fixed_nodes': 4,
    'drop_height': 150,
    'gravity': 2000.0,
    'stiffness': 5000.0,
    'damping': 0.005
}

class ClothApp:
    '''
    Main application class for the cloth simulation.
    '''

    def __init__(self, root):
        self.root = root
        self.root.title("Cloth Simulation - Physics Engine")

        self.mesh = None
        self.physics_running = False
        self.ground_y = 0.0
        self.grabbed_node_idx = None
        self.grabbed_node_was_fixed = False
        self.last_time = time.perf_counter()
        self.accumulator = 0.0
        self.physics_dt = 0.001

        # 1. Initialize GUI
        self.controls = ControlPanel(
            parent=self.root,
            on_generate=self.update_simulation,
            on_toggle=self.toggle_physics,
            on_drop=self._drop_cloth,
            defaults=DEFAULTS
        )

        # 2. Initialize canvas (right panel)
        self.canvas = tk.Canvas(
            self.root,
            width=DEFAULTS['width'] * 1.25, height=DEFAULTS['height'] * 1.25,
            bg="white", highlightthickness=1, highlightbackground="#ccc"
        )
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.cloth_canvas = ClothCanvas(self.canvas)

        self._setup_bindings()
        self.root.update()
        self.update_simulation()
        self._game_loop()

    def _setup_bindings(self):
        '''Function to define the bindings'''

        self.canvas.bind("<MouseWheel>", self.cloth_canvas.handle_zoom)
        self.canvas.bind("<Button-4>", self.cloth_canvas.handle_zoom)
        self.canvas.bind("<Button-5>", self.cloth_canvas.handle_zoom)
        self.canvas.bind("<Shift-Button-1>", self.cloth_canvas.start_pan)
        self.canvas.bind("<Shift-B1-Motion>", self.cloth_canvas.drag_pan)
        self.canvas.bind("<Control-Button-1>", self._handle_mouse_cut)
        self.canvas.bind("<Control-B1-Motion>", self._handle_mouse_cut)

        self.canvas.bind("<Button-1>", self._handle_mouse_grab)
        self.canvas.bind("<B1-Motion>", self._handle_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._handle_mouse_release)

        self.root.bind("<r>", lambda event: self._shortcut_trigger(self.update_simulation))
        self.root.bind("<space>", lambda event: self._shortcut_trigger(self.toggle_physics))
        self.root.bind("<d>", lambda event: self._shortcut_trigger(self._drop_cloth))

        self.root.bind_class("Entry", "<r>",
                            lambda event: self._shortcut_trigger(self.update_simulation))
        self.root.bind_class("Entry", "<space>",
                            lambda event: self._shortcut_trigger(self.toggle_physics))
        self.root.bind_class("Entry", "<d>",
                            lambda event: self._shortcut_trigger(self._drop_cloth))

    def _shortcut_trigger(self, func):
        '''Safely sets focus to root, executes the function, and blocks default entry behavior.'''

        self.root.focus_set()
        func()
        return "break"

    def toggle_physics(self):
        '''Toggles the execution state of the physics engine loop.'''

        self.physics_running = not self.physics_running
        if self.physics_running:
            self.controls.btn_toggle_phys.config(text="PAUSE ENGINE", bg="#FF9800")
            self.last_time = time.perf_counter()
        else:
            self.controls.btn_toggle_phys.config(text="START ENGINE", bg="#2196F3")

    def _handle_mouse_grab(self, event):
        '''Finds and anchors the closest node to the mouse cursor.'''

        if self.mesh is None:
            return

        if (event.state & 0x0001) or (event.state & 0x0004) or getattr(self, 'c_pressed', False):
            return

        wx, wy = self.cloth_canvas.screen_to_world(event.x, event.y)

        distances = np.hypot(self.mesh.pos[:, 0] - wx, self.mesh.pos[:, 1] - wy)
        closest_idx = np.argmin(distances)

        grab_radius = 25.0
        if distances[closest_idx] <= grab_radius:
            self.grabbed_node_idx = closest_idx
            self.grabbed_node_was_fixed = self.mesh.fixed[closest_idx]

            self.mesh.fixed[closest_idx] = True

    def _handle_mouse_drag(self, event):
        '''Updates the grabbed node's position to track the mouse cursor.'''

        if self.mesh is None or self.grabbed_node_idx is None:
            return

        wx, wy = self.cloth_canvas.screen_to_world(event.x, event.y)

        self.mesh.pos[self.grabbed_node_idx] = [wx, wy]

        self.mesh.vel[self.grabbed_node_idx] = [0.0, 0.0]

        if not self.physics_running:
            self.cloth_canvas.draw_mesh(self.mesh, self.ground_y)

    def _handle_mouse_release(self, event):
        '''Releases the grabbed node, restoring its original physics state.'''

        if self.mesh is None or self.grabbed_node_idx is None:
            return

        self.mesh.fixed[self.grabbed_node_idx] = self.grabbed_node_was_fixed

        self.grabbed_node_idx = None

    def _drop_cloth(self):
        '''Unpins all fixed nodes instantly.'''

        if self.mesh is not None:
            self.mesh.fixed[:] = False

    def _handle_mouse_cut(self, event):
        '''Handles cutting springs when clicking/dragging while holding Ctrl.'''

        if self.mesh is None:
            return

        wx, wy = self.cloth_canvas.screen_to_world(event.x, event.y)

        # Cutting radius
        cut_radius = 15.0

        # Find starting and ending position of every spring
        p1 = self.mesh.pos[self.mesh.spring_indices[:, 0]]
        p2 = self.mesh.pos[self.mesh.spring_indices[:, 1]]

        # Compute middle points
        midpoints = (p1 + p2) / 2.0

        # Compute distance from mouse position and springs middle points
        dx = midpoints[:, 0] - wx
        dy = midpoints[:, 1] - wy
        distances = np.hypot(dx, dy)

        # Create mask for springs not in the cutting radius
        mask = distances > cut_radius

        # Apply mask to the mash
        self.mesh.spring_indices = self.mesh.spring_indices[mask]
        self.mesh.rest_lengths = self.mesh.rest_lengths[mask]

        if not self.physics_running:
            self.cloth_canvas.draw_mesh(self.mesh, self.ground_y)

    def update_simulation(self):
        '''
        Updates the cloth simulation based on user input parameters. Pauses the engine,
        generates the new mesh, and resets the camera view.
        '''

        self.physics_running = False
        self.controls.btn_toggle_phys.config(text="START ENGINE", bg="#2196F3")
        self.cloth_canvas.reset_camera()

        try:
            w = int(self.controls.entry_width.get())
            h = int(self.controls.entry_height.get())
            m = float(self.controls.entry_mass.get())
            total = int(self.controls.entry_total_nodes.get())
            fixed = int(self.controls.entry_fixed_nodes.get())
            drop_height = int(self.controls.entry_drop_height.get())
        except ValueError:
            return

        self.canvas.config(width=w * 1.25, height=h * 1.25)
        self.root.update()

        self.mesh = gf.generate_cloth_grid(
            w, h, m, total, fixed, self.canvas.winfo_width(), self.canvas.winfo_height()
        )

        # Compute ground position
        if self.mesh is not None and len(self.mesh.pos) > 0:
            lowest_node_y = self.mesh.pos[:, 1].max()
            self.ground_y = lowest_node_y + drop_height
        else:
            self.ground_y = h + drop_height

        self.cloth_canvas.draw_mesh(self.mesh, self.ground_y)

    def _game_loop(self):
        '''Asynchronous execution loop running at ~60 FPS.'''

        current_time = time.perf_counter()
        frame_time = current_time - self.last_time
        self.last_time = current_time

        frame_time = min(frame_time, 0.1)

        if self.physics_running:
            try:
                g = float(self.controls.entry_gravity.get())
                k = float(self.controls.entry_stiffness.get())
                d = float(self.controls.entry_damping.get())
            except ValueError:
                g, k, d = DEFAULTS['gravity'], DEFAULTS['stiffness'], DEFAULTS['damping']

            self.accumulator += frame_time
            while self.accumulator >= self.physics_dt:
                phys.step_physics(self.mesh, g, k, d, self.ground_y, dt=self.physics_dt)
                self.accumulator -= self.physics_dt

        self.cloth_canvas.draw_mesh(self.mesh, self.ground_y)
        self.root.after(16, self._game_loop)
