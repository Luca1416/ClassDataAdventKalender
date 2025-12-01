import tkinter as tk
import math
import random


class matrics:
    """
    3D matrix demo:
    - Auto mode: continuous rotation using rotation matrices
    - Manual mode: user controls rotation angles
    - Shows current variables in a panel
    """

    def __init__(self, root):
        self.root = root
        self.root.title("3D Matrix Demo – Rotating Cube (Auto & Manual)")
        self.width = 700
        self.height = 700
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)

        # Canvas
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height - 200, bg="black")
        self.canvas.pack(pady=10)

        # --- Mode + buttons ---
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)

        self.mode_var = tk.StringVar(value="auto")
        tk.Radiobutton(mode_frame, text="Auto mode", variable=self.mode_var, value="auto",
                       command=self.on_mode_change).pack(side="left", padx=5)
        tk.Radiobutton(mode_frame, text="Manual mode", variable=self.mode_var, value="manual",
                       command=self.on_mode_change).pack(side="left", padx=5)

        self.btn_toggle = tk.Button(mode_frame, text="Pause", command=self.toggle_animation)
        self.btn_toggle.pack(side="left", padx=10)

        self.btn_random = tk.Button(mode_frame, text="Random orientation", command=self.randomize_orientation)
        self.btn_random.pack(side="left", padx=5)

        # blank Save Program button
        tk.Button(mode_frame, text="Save Program", command=self.save_program_placeholder).pack(side="left", padx=15)

        # --- Controls: auto + manual ---
        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=5, fill="x")

        # Auto controls
        auto_frame = tk.LabelFrame(controls_frame, text="Auto rotation")
        auto_frame.pack(side="left", padx=10, fill="y")

        tk.Label(auto_frame, text="Rotation speed:").pack(anchor="w")
        self.speed_scale = tk.Scale(auto_frame, from_=0, to=0.1, resolution=0.005,
                                    orient="horizontal", length=180)
        self.speed_scale.set(0.03)
        self.speed_scale.pack()

        # Manual controls
        manual_frame = tk.LabelFrame(controls_frame, text="Manual rotation (degrees)")
        manual_frame.pack(side="left", padx=10, fill="y")

        self.slider_ax = tk.Scale(manual_frame, from_=0, to=360, resolution=1,
                                  orient="horizontal", label="Angle X", length=180,
                                  command=self.on_manual_angles_change)
        self.slider_ax.pack()
        self.slider_ay = tk.Scale(manual_frame, from_=0, to=360, resolution=1,
                                  orient="horizontal", label="Angle Y", length=180,
                                  command=self.on_manual_angles_change)
        self.slider_ay.pack()
        self.slider_az = tk.Scale(manual_frame, from_=0, to=360, resolution=1,
                                  orient="horizontal", label="Angle Z", length=180,
                                  command=self.on_manual_angles_change)
        self.slider_az.pack()

        # --- Variables panel ---
        vars_frame = tk.LabelFrame(self.root, text="Variables")
        vars_frame.pack(pady=5, fill="x", padx=10)

        self.label_vars = tk.Label(vars_frame, text="", justify="left", anchor="w", font=("Courier New", 9))
        self.label_vars.pack(fill="x")

        # --- Info text ---
        info = (
            "3D matrices in action:\n"
            "  • Rotation: v' = R · v, where R = Rz · Ry · Rx\n"
            "  • Projection: (x, y, z) → (x_screen, y_screen) using perspective\n"
            "Each corner of the cube is transformed by these matrices every frame."
        )
        self.label_info = tk.Label(self.root, text=info, justify="left")
        self.label_info.pack(pady=5)

        # Cube data
        s = 1
        self.vertices = [
            (-s, -s, -s),
            ( s, -s, -s),
            ( s,  s, -s),
            (-s,  s, -s),
            (-s, -s,  s),
            ( s, -s,  s),
            ( s,  s,  s),
            (-s,  s,  s),
        ]

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]

        # Angles (radians)
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0

        # Projection settings
        self.fov = 300
        self.dist = 3

        # Animation state
        self.running = True  # play/pause
        self.animate()

        # Start with manual sliders synced to initial angles
        self.sync_sliders_from_angles()
        self.on_mode_change()

    # ---------------------- Math helpers ----------------------

    def rotate_point(self, x, y, z, ax, ay, az):
        """Rotate point (x,y,z) by angles ax, ay, az around x,y,z axes."""
        cx, sx = math.cos(ax), math.sin(ax)
        cy, sy = math.cos(ay), math.sin(ay)
        cz, sz = math.cos(az), math.sin(az)

        # Rx
        y1 = y * cx - z * sx
        z1 = y * sx + z * cx
        x1 = x

        # Ry
        x2 = x1 * cy + z1 * sy
        z2 = -x1 * sy + z1 * cy
        y2 = y1

        # Rz
        x3 = x2 * cz - y2 * sz
        y3 = x2 * sz + y2 * cz
        z3 = z2

        return x3, y3, z3

    def project_point(self, x, y, z):
        """Project 3D point to 2D via perspective."""
        z += self.dist
        if z == 0:
            z = 1e-6
        factor = self.fov / z
        sx = x * factor + self.width / 2
        sy = -y * factor + (self.height - 200) / 2
        return sx, sy

    # ---------------------- Drawing & animation ----------------------

    def draw_cube(self):
        self.canvas.delete("all")

        transformed = []
        for (x, y, z) in self.vertices:
            xr, yr, zr = self.rotate_point(x, y, z, self.angle_x, self.angle_y, self.angle_z)
            transformed.append((xr, yr, zr))

        projected = []
        for (x, y, z) in transformed:
            sx, sy = self.project_point(x, y, z)
            projected.append((sx, sy))

        # Cube edges
        for (i, j) in self.edges:
            x1, y1 = projected[i]
            x2, y2 = projected[j]
            self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

        # Axes
        axes_len = 2
        axes = [
            ((0, 0, 0), (axes_len, 0, 0), "red"),    # X
            ((0, 0, 0), (0, axes_len, 0), "green"),  # Y
            ((0, 0, 0), (0, 0, axes_len), "blue"),   # Z
        ]
        for (p1, p2, color) in axes:
            xr1, yr1, zr1 = self.rotate_point(*p1, self.angle_x, self.angle_y, self.angle_z)
            xr2, yr2, zr2 = self.rotate_point(*p2, self.angle_x, self.angle_y, self.angle_z)
            sx1, sy1 = self.project_point(xr1, yr1, zr1)
            sx2, sy2 = self.project_point(xr2, yr2, zr2)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=2)

        self.update_variables_label()

    def animate(self):
        if self.running and self.mode_var.get() == "auto":
            speed = self.speed_scale.get()
            self.angle_x += speed * 0.7
            self.angle_y += speed * 1.0
            self.angle_z += speed * 0.4

        self.draw_cube()
        self.root.after(16, self.animate)  # ~60 FPS

    # ---------------------- Mode & controls ----------------------

    def toggle_animation(self):
        self.running = not self.running
        self.btn_toggle.config(text="Pause" if self.running else "Start")

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "auto":
            # Auto: speed slider enabled, manual sliders "view-only" (but still update if we want)
            self.speed_scale.config(state="normal")
            self.slider_ax.config(state="disabled")
            self.slider_ay.config(state="disabled")
            self.slider_az.config(state="disabled")
        else:
            # Manual
            self.speed_scale.config(state="disabled")
            self.slider_ax.config(state="normal")
            self.slider_ay.config(state="normal")
            self.slider_az.config(state="normal")
            # Keep angles synced with sliders
            self.sync_sliders_from_angles()

    def sync_sliders_from_angles(self):
        ax_deg = math.degrees(self.angle_x) % 360
        ay_deg = math.degrees(self.angle_y) % 360
        az_deg = math.degrees(self.angle_z) % 360
        self.slider_ax.set(ax_deg)
        self.slider_ay.set(ay_deg)
        self.slider_az.set(az_deg)

    def on_manual_angles_change(self, _val=None):
        if self.mode_var.get() != "manual":
            return
        ax_deg = self.slider_ax.get()
        ay_deg = self.slider_ay.get()
        az_deg = self.slider_az.get()
        self.angle_x = math.radians(ax_deg)
        self.angle_y = math.radians(ay_deg)
        self.angle_z = math.radians(az_deg)
        self.draw_cube()

    def randomize_orientation(self):
        self.angle_x = random.uniform(0, 2 * math.pi)
        self.angle_y = random.uniform(0, 2 * math.pi)
        self.angle_z = random.uniform(0, 2 * math.pi)
        if self.mode_var.get() == "manual":
            self.sync_sliders_from_angles()

    # ---------------------- Variables display ----------------------

    def update_variables_label(self):
        ax_deg = math.degrees(self.angle_x) % 360
        ay_deg = math.degrees(self.angle_y) % 360
        az_deg = math.degrees(self.angle_z) % 360
        speed = self.speed_scale.get()
        text = (
            f"mode     : {self.mode_var.get()}\n"
            f"angle_x  : {ax_deg:7.2f}°\n"
            f"angle_y  : {ay_deg:7.2f}°\n"
            f"angle_z  : {az_deg:7.2f}°\n"
            f"speed    : {speed:7.3f} (auto mode only)\n"
            f"fov      : {self.fov:7.1f}\n"
            f"dist     : {self.dist:7.2f}\n"
        )
        self.label_vars.config(text=text)

    # ---------------------- Misc ----------------------

    def save_program_placeholder(self):
        # intentionally does nothing
        pass


def main():
    root = tk.Tk()
    app = matrics(root)
    root.mainloop()


if __name__ == "__main__":
    main()
