'''
Main entry point for the cloth simulation application. This script initializes the GUI, 
sets up the canvas, and manages user interactions for simulating cloth physics.
'''

from dataclasses import dataclass
import time
import tkinter as tk
from proj.canvas import ClothCanvas
import proj.engine as phys
import proj.utils as gf

# Default parameters
DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 400
DEFAULT_WEIGHT = 100.0
DEFAULT_TOTAL_NODES = 500
DEFAULT_FIXED_NODES = 4


@dataclass
class ClothApp:
    '''
    Main application class for the cloth simulation. It handles the GUI setup, user input,
    and updates the simulation physics engine based on user-defined parameters.
    '''

    def __init__(self, root):

        self.root = root
        self.root.title("Cloth Simulation - Physics Engine")

        self.nodes_grid = []
        self.springs_list = []
        self.physics_running = False

        self.last_time = time.perf_counter()
        self.accumulator = 0.0
        self.physics_dt = 0.001

        # 1. Generate the GUI components
        self._build_gui()

        # 2. Generate the ClothCanvas instance for drawing and interaction
        self.cloth_canvas = ClothCanvas(self.canvas)

        self._setup_bindings()

        # Initial startup
        self.root.update()
        self.update_simulation()
        self._game_loop()

    def _build_gui(self):
        '''Builds the GUI layout with control panels and canvas.'''

        # Left Panel: Geometry controls
        control_frame = tk.LabelFrame(
            self.root, text=" Cloth Geometry ", padx=10, pady=10
        )
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)

        tk.Label(control_frame, text="Width (px):").pack(anchor=tk.W)
        self.entry_width = tk.Entry(control_frame, width=15)
        self.entry_width.insert(0, str(DEFAULT_WIDTH))
        self.entry_width.pack(pady=(0, 10))

        tk.Label(control_frame, text="Height (px):").pack(anchor=tk.W)
        self.entry_height = tk.Entry(control_frame, width=15)
        self.entry_height.insert(0, str(DEFAULT_HEIGHT))
        self.entry_height.pack(pady=(0, 10))

        tk.Label(control_frame, text="Mass:").pack(anchor=tk.W)
        self.entry_mass = tk.Entry(control_frame, width=15)
        self.entry_mass.insert(0, str(DEFAULT_WEIGHT))
        self.entry_mass.pack(pady=(0, 10))

        tk.Label(control_frame, text="Total Nodes:").pack(anchor=tk.W)
        self.entry_total_nodes = tk.Entry(control_frame, width=15)
        self.entry_total_nodes.insert(0, str(DEFAULT_TOTAL_NODES))
        self.entry_total_nodes.pack(pady=(0, 10))

        tk.Label(control_frame, text="Fixed Nodes:").pack(anchor=tk.W)
        self.entry_fixed_nodes = tk.Entry(control_frame, width=15)
        self.entry_fixed_nodes.insert(0, str(DEFAULT_FIXED_NODES))
        self.entry_fixed_nodes.pack(pady=(0, 15))

        btn_update = tk.Button(
            control_frame,
            text="Generate Grid",
            command=self.update_simulation,
            bg="#4CAF50",
            fg="white",
        )
        btn_update.pack(fill=tk.X)

        # Center Panel: Physics controls
        phys_frame = tk.LabelFrame(
            self.root, text=" Physics Parameters ", padx=10, pady=10
        )
        phys_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)

        tk.Label(phys_frame, text="Gravity (px/s²):").pack(anchor=tk.W)
        self.entry_gravity = tk.Entry(phys_frame, width=15)
        self.entry_gravity.insert(0, "2000.0")
        self.entry_gravity.pack(pady=(0, 10))

        tk.Label(phys_frame, text="Stiffness (k):").pack(anchor=tk.W)
        self.entry_stiffness = tk.Entry(phys_frame, width=15)
        self.entry_stiffness.insert(0, "5000.0")
        self.entry_stiffness.pack(pady=(0, 10))

        tk.Label(phys_frame, text="Damping:").pack(anchor=tk.W)
        self.entry_damping = tk.Entry(phys_frame, width=15)
        self.entry_damping.insert(0, "0.005")
        self.entry_damping.pack(pady=(0, 15))

        self.btn_toggle_phys = tk.Button(
            phys_frame,
            text="START ENGINE",
            command=self.toggle_physics,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        self.btn_toggle_phys.pack(fill=tk.X)

        tk.Label(
            phys_frame,
            text="\n💡 Controls:\n" \
            "• Zoom: Wheel\n" \
            "• Pan: Shift + Click & Drag\n" \
            "• Reset grid: r\n" \
            "• Start/Pause engine: Space",
            justify=tk.LEFT,
            fg="gray",
        ).pack()

        # Right Panel: Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=DEFAULT_WIDTH * 1.25,
            height=DEFAULT_HEIGHT * 1.25,
            bg="white",
            highlightthickness=1,
            highlightbackground="#ccc",
        )
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

    def _setup_bindings(self):
        self.canvas.bind("<MouseWheel>", self.cloth_canvas.handle_zoom)
        self.canvas.bind("<Button-4>", self.cloth_canvas.handle_zoom)
        self.canvas.bind("<Button-5>", self.cloth_canvas.handle_zoom)
        self.canvas.bind("<Shift-Button-1>", self.cloth_canvas.start_pan)
        self.canvas.bind("<Shift-B1-Motion>", self.cloth_canvas.drag_pan)
   
        self.root.bind_class("Entry", "<r>", self._on_restart_pressed)
        self.root.bind_class("Entry", "<space>", self._on_toggle_pressed)

        # Aggiungi anche questi per quando il focus NON è sulle entry (es. sul canvas)
        self.root.bind("<r>", self._on_restart_pressed)
        self.root.bind("<space>", self._on_toggle_pressed)

    def _on_restart_pressed(self, event):
        '''Handles the restart button press event. Resets the simulation and camera view.'''

        self.root.focus_set()
        self.update_simulation()

        return "break"

    def _on_toggle_pressed(self, event):
        '''Handles the toggle button press event. Starts or pauses the physics engine loop.'''

        self.root.focus_set()
        self.toggle_physics()

        return "break"

    def toggle_physics(self):
        '''Toggles the execution state of the physics engine loop.'''

        self.physics_running = not self.physics_running
        if self.physics_running:
            self.btn_toggle_phys.config(text="PAUSE ENGINE", bg="#FF9800")
            self.last_time = time.perf_counter()
        else:
            self.btn_toggle_phys.config(text="START ENGINE", bg="#2196F3")

    def update_simulation(self):
        '''
        Updates the cloth simulation based on user input parameters. Pauses the engine,
        generates the new mesh, and resets the camera view.
        '''

        self.physics_running = False
        self.btn_toggle_phys.config(text="START ENGINE", bg="#2196F3")
        self.cloth_canvas.reset_camera()

        try:
            w = int(self.entry_width.get())
            h = int(self.entry_height.get())
            m = float(self.entry_mass.get())
            total = int(self.entry_total_nodes.get())
            fixed = int(self.entry_fixed_nodes.get())
        except ValueError:
            return

        self.canvas.config(width=w * 1.25, height=h * 1.25)
        self.root.update()

        self.nodes_grid, self.springs_list = gf.generate_cloth_grid(
            w, h, m, total, fixed, self.canvas.winfo_width(), self.canvas.winfo_height()
        )
        self.cloth_canvas.draw_nodes(self.nodes_grid, self.springs_list)

    def _game_loop(self):
        '''Asynchronous execution loop running at ~60 FPS.'''

        # 1. Calcola il tempo reale trascorso (Delta Time)
        current_time = time.perf_counter()
        frame_time = current_time - self.last_time
        self.last_time = current_time

        # "Spiral of death" protection: se l'utente sposta la finestra 
        # e il gioco lagga per 2 secondi, facciamo finta siano passati max 100ms
        if frame_time > 0.1:
            frame_time = 0.1

        if self.physics_running:
            try:
                g = float(self.entry_gravity.get())
                k = float(self.entry_stiffness.get())
                d = float(self.entry_damping.get())
                m = float(self.entry_mass.get())
            except ValueError:
                g, k, d = 2000.0, 5000.0, 0.005

            # Getta il tempo reale nel "secchio"
            self.accumulator += frame_time

            # Consuma il secchio a morsi rigorosamente identici (self.physics_dt)
            while self.accumulator >= self.physics_dt:
                phys.step_physics(
                    self.nodes_grid,
                    self.springs_list,
                    g,
                    k,
                    d,
                    dt=self.physics_dt,  # <-- Passiamo il dt fisso di 0.002!
                )
                self.accumulator -= self.physics_dt

        # 2. Il Canvas viene disegnato SEMPRE E SOLO una volta per frame visivo
        self.cloth_canvas.draw_nodes(self.nodes_grid, self.springs_list)
        self.root.after(16, self._game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClothApp(root)
    root.mainloop()
