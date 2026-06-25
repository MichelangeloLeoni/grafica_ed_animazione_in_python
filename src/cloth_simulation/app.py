'''
Core application script containing the ClothApp class which manages the application state,
shortcuts, and orchestrates the rendering and physics loops.
'''
import time
import tkinter as tk
from cloth_simulation.canvas import ClothCanvas
from cloth_simulation.ui_panels import ControlPanel
import cloth_simulation.engine as phys
import cloth_simulation.utils as gf

DEFAULTS = {
    'width': 400,
    'height': 400,
    'mass': 100.0,
    'total_nodes': 500,
    'fixed_nodes': 4
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
        self.last_time = time.perf_counter()
        self.accumulator = 0.0
        self.physics_dt = 0.001

        # 1. Initialize GUI
        self.controls = ControlPanel(
            parent=self.root,
            on_generate=self.update_simulation,
            on_toggle=self.toggle_physics,
            on_drop=self.drop_cloth,
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

        self.root.bind("<r>", lambda event: self._shortcut_trigger(self.update_simulation))
        self.root.bind("<space>", lambda event: self._shortcut_trigger(self.toggle_physics))
        self.root.bind("<d>", lambda event: self._shortcut_trigger(self.drop_cloth))

        self.root.bind_class("Entry", "<r>",
                            lambda event: self._shortcut_trigger(self.update_simulation))
        self.root.bind_class("Entry", "<space>",
                            lambda event: self._shortcut_trigger(self.toggle_physics))
        self.root.bind_class("Entry", "<d>",
                            lambda event: self._shortcut_trigger(self.drop_cloth))

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

    def drop_cloth(self):
        '''Unpins all fixed nodes instantly.'''

        if self.mesh is not None:
            self.mesh.fixed[:] = False

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
        except ValueError:
            return

        self.canvas.config(width=w * 1.25, height=h * 1.25)
        self.root.update()

        self.mesh = gf.generate_cloth_grid(
            w, h, m, total, fixed, self.canvas.winfo_width(), self.canvas.winfo_height()
        )
        self.cloth_canvas.draw_mesh(self.mesh)

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
                g, k, d = 2000.0, 5000.0, 0.005

            self.accumulator += frame_time
            while self.accumulator >= self.physics_dt:
                phys.step_physics(self.mesh, g, k, d, dt=self.physics_dt)
                self.accumulator -= self.physics_dt

        self.cloth_canvas.draw_mesh(self.mesh)
        self.root.after(16, self._game_loop)
