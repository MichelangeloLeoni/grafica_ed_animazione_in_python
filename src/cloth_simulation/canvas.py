'''
Script that defines the ClothCanvas class, which encapsulates the logic for drawing nodes and 
springs on a Tkinter canvas, as well as handling zooming and panning interactions via a 2D camera.
'''

NODE_RADIUS = 5


class ClothCanvas:
    '''
    Class that manages the drawing of nodes and springs on a Tkinter canvas. It provides methods
    for rendering the cloth simulation, handling zoom and pan interactions via an internal camera,
    and projecting world coordinates to screen space.
    '''

    def __init__(self, canvas_obj, plot_obj):
        self.canvas = canvas_obj
        self.plot = plot_obj
        self.zoom = 1.0
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.pan_start_x = 0
        self.pan_start_y = 0

        self.energy_history = []
        self.max_history_points = 400

    def reset_camera(self):
        '''Resets the internal camera view to default values.'''

        self.zoom = 1.0
        self.cam_x = 0.0
        self.cam_y = 0.0

    def world_to_screen(self, x, y):
        '''Projects physical world coordinates onto canvas screen coordinates.'''

        sx = (x + self.cam_x) * self.zoom
        sy = (y + self.cam_y) * self.zoom
        return sx, sy

    def screen_to_world(self, sx, sy):
        '''Converts screen canvas coordinates back to physical world coordinates.'''

        x = (sx / self.zoom) - self.cam_x
        y = (sy / self.zoom) - self.cam_y
        return x, y

    def draw_mesh(self, mesh, ground_y):
        '''
        Draws the nodes and springs on the canvas using NumPy arrays and projected coordinates.
        '''

        self.canvas.delete("all")

        if mesh is None:
            return

        # 1. Draw ground
        if ground_y is not None:
            _, sy = self.world_to_screen(0, ground_y)
            canvas_width = self.canvas.winfo_width()
            self.canvas.create_line(
                0, sy, canvas_width, sy, fill="#4CAF50", width=3
            )

        line_width = max(1, int(self.zoom))
        pos = mesh.pos
        spring_indices = mesh.spring_indices

        # 2. Draw spring
        for i in range(len(spring_indices)):
            p1_idx = spring_indices[i, 0]
            p2_idx = spring_indices[i, 1]

            x1, y1 = self.world_to_screen(pos[p1_idx, 0], pos[p1_idx, 1])
            x2, y2 = self.world_to_screen(pos[p2_idx, 0], pos[p2_idx, 1])

            self.canvas.create_line(
                x1, y1, x2, y2, fill="#bbb", width=line_width
            )

        # 3. Draw nodes
        scaled_radius = max(2, int(NODE_RADIUS * self.zoom))
        fixed = mesh.fixed

        for i in range(len(pos)):
            sx, sy = self.world_to_screen(pos[i, 0], pos[i, 1])
            color = "red" if fixed[i] else "blue"
            self.canvas.create_oval(
                sx - scaled_radius,
                sy - scaled_radius,
                sx + scaled_radius,
                sy + scaled_radius,
                fill=color,
                outline="",
            )

    def handle_zoom(self, event):
        '''Handles zooming in and out of the canvas centered on the mouse position.'''

        old_zoom = self.zoom
        if event.num == 4 or event.delta > 0:
            self.zoom *= 1.1
        elif event.num == 5 or event.delta < 0:
            self.zoom *= 0.9

        self.zoom = max(0.2, min(5.0, self.zoom))

        # Re-center camera offset towards the mouse pointer
        self.cam_x = (self.cam_x - event.x / old_zoom) + (event.x / self.zoom)
        self.cam_y = (self.cam_y - event.y / old_zoom) + (event.y / self.zoom)

    def start_pan(self, event):
        '''Initializes the starting point for panning the canvas.'''

        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def drag_pan(self, event):
        '''Moves the camera view across the world space during dragging.'''

        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.cam_x += dx / self.zoom
        self.cam_y += dy / self.zoom
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def draw_graph(self, current_energy):
        '''
        Disegna un grafico lineare dell'energia in tempo reale sul canvas dedicato,
        applicando un auto-scaling verticale basato sui valori minimi e massimi.
        '''
        # 1. Salva il dato nella cronologia
        self.energy_history.append(current_energy)
        if len(self.energy_history) > self.max_history_points:
            self.energy_history.pop(0)

        # 2. Pulisci il canvas del grafico
        self.plot.delete("all")

        num_points = len(self.energy_history)
        if num_points < 2:
            return

        # Recupera le dimensioni attuali del widget
        w = self.plot.winfo_width()
        h = self.plot.winfo_height()
        
        # Margini interni per evitare che il grafico tocchi i bordi
        padding_x = 10
        padding_y = 25
        graph_w = w - (padding_x * 2)
        graph_h = h - (padding_y * 2)

        # 3. Calcola Min e Max per l'auto-scaling verticale
        min_e = min(self.energy_history)
        max_e = max(self.energy_history)
        energy_range = max_e - min_e
        if energy_range == 0: 
            energy_range = 1.0  # Previene la divisione per zero se l'energia è costante

        # 4. Genera le coordinate e disegna i segmenti del grafico
        points = []
        for i in range(num_points):
            # Mappatura asse X (tempo/frame)
            x = padding_x + (i / (self.max_history_points - 1)) * graph_w
            
            # Mappatura asse Y (Valore Energia - invertito perché la Y di Tkinter va verso il basso)
            norm_y = (self.energy_history[i] - min_e) / energy_range
            y = padding_y + graph_h * (1.0 - norm_y)
            
            points.append((x, y))

        # Disegna la linea continua del grafico
        for i in range(num_points - 1):
            self.plot.create_line(
                points[i][0], points[i][1], points[i+1][0], points[i+1][1],
                fill="#E91E63", width=2
            )

        # 5. Sovrapponi informazioni testuali di diagnostica
        # Convertiamo l'energia da Pixel-Joules a Joule reali (dividendo per PIXELS_TO_METERS^2, ipotizzando 100)
        conversion_factor = 100.0 ** 2
        current_j = current_energy / conversion_factor
        max_j = max_e / conversion_factor
        min_j = min_e / conversion_factor

        self.plot.create_text(
            padding_x, 12, anchor="w", fill="#333", font=("Courier", 10, "bold"),
            text=f"ENERGIA TOTALE: {current_j:.4f} J  [Min: {min_j:.3f} J | Max: {max_j:.3f} J]"
        )
