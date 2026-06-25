'''
Script that defines the ControlPanel class, encapsulating all Tkinter 
widgets, inputs, and layouts for the cloth simulation settings.
'''
from dataclasses import dataclass
import tkinter as tk

@dataclass
class ControlPanel:
    '''
    Handles the creation and layout of the geometry and physics control panels.
    Expects callbacks for the buttons to keep UI separated from application logic.
    '''

    def __init__(self, parent, on_generate, on_toggle, on_drop, defaults):
        self.parent = parent

        # Left panel (cloth geometry)
        control_frame = tk.LabelFrame(self.parent, text=" Cloth Geometry ", padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)

        tk.Label(control_frame, text="Width (px):").pack(anchor=tk.W)
        self.entry_width = tk.Entry(control_frame, width=15)
        self.entry_width.insert(0, str(defaults['width']))
        self.entry_width.pack(pady=(0, 10))

        tk.Label(control_frame, text="Height (px):").pack(anchor=tk.W)
        self.entry_height = tk.Entry(control_frame, width=15)
        self.entry_height.insert(0, str(defaults['height']))
        self.entry_height.pack(pady=(0, 10))

        tk.Label(control_frame, text="Drop height (px):").pack(anchor=tk.W)
        self.entry_drop_height = tk.Entry(control_frame, width=15)
        self.entry_drop_height.insert(0, str(defaults['drop_height']))
        self.entry_drop_height.pack(pady=(0, 15))

        tk.Label(control_frame, text="Mass:").pack(anchor=tk.W)
        self.entry_mass = tk.Entry(control_frame, width=15)
        self.entry_mass.insert(0, str(defaults['mass']))
        self.entry_mass.pack(pady=(0, 10))

        tk.Label(control_frame, text="Total Nodes:").pack(anchor=tk.W)
        self.entry_total_nodes = tk.Entry(control_frame, width=15)
        self.entry_total_nodes.insert(0, str(defaults['total_nodes']))
        self.entry_total_nodes.pack(pady=(0, 10))

        tk.Label(control_frame, text="Fixed Nodes:").pack(anchor=tk.W)
        self.entry_fixed_nodes = tk.Entry(control_frame, width=15)
        self.entry_fixed_nodes.insert(0, str(defaults['fixed_nodes']))
        self.entry_fixed_nodes.pack(pady=(0, 15))

        btn_update = tk.Button(
            control_frame, text="Generate Grid", command=on_generate, bg="#4CAF50", fg="white"
        )
        btn_update.pack(fill=tk.X)

        # Central panel (physics parameters)
        phys_frame = tk.LabelFrame(self.parent, text=" Physics Parameters ", padx=10, pady=10)
        phys_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)

        tk.Label(phys_frame, text="Gravity:").pack(anchor=tk.W)
        self.entry_gravity = tk.Entry(phys_frame, width=15)
        self.entry_gravity.insert(0, str(defaults['gravity']))
        self.entry_gravity.pack(pady=(0, 10))

        tk.Label(phys_frame, text="Stiffness:").pack(anchor=tk.W)
        self.entry_stiffness = tk.Entry(phys_frame, width=15)
        self.entry_stiffness.insert(0, str(defaults['stiffness']))
        self.entry_stiffness.pack(pady=(0, 10))

        tk.Label(phys_frame, text="Damping:").pack(anchor=tk.W)
        self.entry_damping = tk.Entry(phys_frame, width=15)
        self.entry_damping.insert(0, str(defaults['damping']))
        self.entry_damping.pack(pady=(0, 15))

        self.btn_toggle_phys = tk.Button(
            phys_frame, text="START ENGINE", command=on_toggle,
            bg="#2196F3", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_toggle_phys.pack(fill=tk.X)

        self.btn_drop = tk.Button(
            phys_frame, text="DROP CLOTH", command=on_drop,
            bg="#f44336", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_drop.pack(fill=tk.X, pady=(5, 0))

        tk.Label(
            phys_frame,
            text="\n💡 Controls:\n" \
            "• Zoom: Wheel\n" \
            "• Pan: Shift + Click & Drag\n" \
            "• Reset grid: r\n" \
            "• Start/Pause engine: Space\n" \
            "• Drop the cloth",
            justify=tk.LEFT,
            fg="gray",
        ).pack()
