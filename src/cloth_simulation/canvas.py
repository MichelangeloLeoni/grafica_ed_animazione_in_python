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

    def __init__(self, canvas_obj):

        self.canvas = canvas_obj
        self.zoom = 1.0
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.pan_start_x = 0
        self.pan_start_y = 0

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

    def draw_nodes(self, nodes_matrix, springs_list):
        '''Draws the nodes and springs on the canvas using projected camera coordinates.'''

        self.canvas.delete("all")

        line_width = max(1, int(self.zoom))
        for spring in springs_list:
            x1, y1 = self.world_to_screen(spring.p1.x, spring.p1.y)
            x2, y2 = self.world_to_screen(spring.p2.x, spring.p2.y)
            color = "#bbb" if spring.spring_type == "structural" else "#eee"
            self.canvas.create_line(
                x1, y1, x2, y2, fill=color, width=line_width
            )

        scaled_radius = max(2, int(NODE_RADIUS * self.zoom))
        for row in nodes_matrix:
            for node in row:
                sx, sy = self.world_to_screen(node.x, node.y)
                color = "red" if node.fixed else "blue"
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
