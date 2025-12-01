import os
import sys
import math
import time
import random
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from scipy.spatial import KDTree
from PIL import Image


class PixelMorphApp(tk.Tk):
    BLOCK_SIZE = 2
    INITIAL_DELAY_MS = 2000
    CHAOS_DURATION_MS = 2000
    TIMER_INTERVAL_MS = 16

    class PixelObj:
        def __init__(self, current, target, chaos_target, color, size, canvas_id=None):
            self.current = list(current)
            self.target = list(target)
            self.chaos_target = list(chaos_target)
            self.color = color
            self.size = size
            self.canvas_id = canvas_id

    def __init__(self):
        super().__init__()

        self.title("Pixel Morph Demo")
        self.resizable(False, False)

        self.pixels = []
        self.margin = 100
        self.start_time = None
        self.animation_after_id = None
        self.image_width = 0
        self.image_height = 0

        # UI
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.source_path_var = tk.StringVar()
        self.target_path_var = tk.StringVar()

        tk.Label(control_frame, text="From:").grid(row=0, column=0, sticky="e")
        tk.Entry(control_frame, textvariable=self.source_path_var, width=50).grid(row=0, column=1, padx=5)
        tk.Button(control_frame, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=5)

        tk.Label(control_frame, text="To:").grid(row=1, column=0, sticky="e")
        tk.Entry(control_frame, textvariable=self.target_path_var, width=50).grid(row=1, column=1, padx=5)
        tk.Button(control_frame, text="Browse", command=self.browse_target).grid(row=1, column=2, padx=5)

        button_frame = tk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=8, sticky="w")

        tk.Button(button_frame, text="Start", command=self.start_morph).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Program", command=self.on_save_program).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Quit", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self, width=640, height=480, bg="black")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

    # --- UI handlers ---

    def browse_source(self):
        path = filedialog.askopenfilename(
            title="Choose source image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.source_path_var.set(path)

    def browse_target(self):
        path = filedialog.askopenfilename(
            title="Choose target image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.target_path_var.set(path)

    def on_save_program(self):
        pass  # intentionally empty

    # --- main morphing logic ---

    def start_morph(self):
        source_path = self.source_path_var.get().strip()
        target_path = self.target_path_var.get().strip()

        if not source_path or not target_path:
            messagebox.showerror("Error", "Please select both a source and target image.")
            return

        if not os.path.exists(source_path) or not os.path.exists(target_path):
            messagebox.showerror("Error", "One of the image paths is invalid.")
            return

        try:
            source = Image.open(source_path).convert("RGB")
            target = Image.open(target_path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load images:\n{e}")
            return

        # Resize source to match target
        self.image_width, self.image_height = target.size
        source = source.resize((self.image_width, self.image_height), Image.NEAREST)

        # Resize canvas
        canvas_w = self.image_width * 2 + self.margin * 3
        canvas_h = self.image_height + self.margin * 2
        self.canvas.config(width=canvas_w, height=canvas_h)
        self.canvas.delete("all")

        # Get blocks
        src_blocks = self.get_blocks(source)
        tgt_blocks = self.get_blocks(target)

        src_colors = np.array([c for (_, c) in src_blocks], dtype=np.float32)
        tgt_colors = np.array([c for (_, c) in tgt_blocks], dtype=np.float32)

        # Fast nearest-color matching via k-d tree
        tree = KDTree(tgt_colors)
        dists, indices = tree.query(src_colors)

        rnd = random.Random()
        self.pixels = []

        for i, s in enumerate(indices):
            (sx, sy), scol = src_blocks[i]
            (tx, ty), _ = tgt_blocks[s]

            start_pos = (sx + self.margin, sy + self.margin)
            target_pos = (tx + self.image_width + self.margin * 2, ty + self.margin)

            chaos = (
                target_pos[0] + rnd.randint(-50, 50),
                target_pos[1] + rnd.randint(-50, 50)
            )

            self.pixels.append(
                self.PixelObj(
                    current=start_pos,
                    target=target_pos,
                    chaos_target=chaos,
                    color=scol,  # stays exactly source color
                    size=self.BLOCK_SIZE
                )
            )

        self.create_canvas_items()
        self.update_canvas_items()
        self.update_idletasks()

        self.start_time = time.time()
        self.animation_after_id = self.after(self.TIMER_INTERVAL_MS, self.update_animation)

    def get_blocks(self, img):
        w, h = img.size
        step = self.BLOCK_SIZE
        blocks = []
        for y in range(0, h, step):
            for x in range(0, w, step):
                blocks.append(((x, y), img.getpixel((x, y))))
        return blocks

    # --- canvas handling ---

    def create_canvas_items(self):
        for px in self.pixels:
            x, y = px.current
            s = px.size
            r, g, b = px.color
            col = f"#{r:02x}{g:02x}{b:02x}"
            px.canvas_id = self.canvas.create_rectangle(
                x, y, x + s, y + s, fill=col, outline=col
            )

    def update_canvas_items(self):
        for px in self.pixels:
            if px.canvas_id is None:
                continue
            x, y = px.current
            s = px.size
            self.canvas.coords(px.canvas_id, x, y, x + s, y + s)

    # --- animation loop ---

    def update_animation(self):
        elapsed = (time.time() - self.start_time) * 1000.0

        for px in self.pixels:
            if elapsed < self.INITIAL_DELAY_MS:
                continue

            elif elapsed < self.INITIAL_DELAY_MS + self.CHAOS_DURATION_MS:
                px.current[0] += (px.chaos_target[0] - px.current[0]) * 0.02
                px.current[1] += (px.chaos_target[1] - px.current[1]) * 0.02

            else:
                px.current[0] += (px.target[0] - px.current[0]) * 0.05
                px.current[1] += (px.target[1] - px.current[1]) * 0.05

        self.update_canvas_items()
        self.animation_after_id = self.after(self.TIMER_INTERVAL_MS, self.update_animation)


if __name__ == "__main__":
    PixelMorphApp().mainloop()
