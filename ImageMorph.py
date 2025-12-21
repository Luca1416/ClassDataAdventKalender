import os
import math
import random
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from PIL import Image


class PixelMorphApp(tk.Toplevel):
    BLOCK_SIZE = 2
    MAX_BLOCKS = 5500  # cap rendered rectangles to avoid UI freeze/crash
    INITIAL_DELAY_MS = 2000
    CHAOS_DURATION_MS = 2000
    TIMER_INTERVAL_MS = 16  # ~60 fps similar to the C# sample
    CHAOS_SPREAD = 50  # pixel jitter around target to add mild motion

    class PixelObj:
        def __init__(self, current, target, chaos_target, color, size, canvas_id=None):
            self.current = list(current)
            self.target = list(target)
            self.chaos_target = list(chaos_target)
            self.color = color
            self.size = size
            self.canvas_id = canvas_id

    def __init__(self, master=None):
        # Prefer the existing default root (calendar UI) if available.
        # Only create a hidden root when none exists so we can run standalone.
        self._owned_root = None
        if master is None:
            existing_root = tk._default_root  # avoid auto-creating a root (so run() knows to mainloop)
            if existing_root is None:
                self._owned_root = tk.Tk()
                self._owned_root.withdraw()
                master = self._owned_root
            else:
                master = existing_root

        super().__init__(master)

        self.title("Pixel Morph Demo")
        self.resizable(False, False)

        self.pixels = []
        self.start_time = None
        self.margin = 100
        self.animation_after_id = None
        self.image_width = 0
        self.image_height = 0

        # UI
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.source_path_var = tk.StringVar(master=self)
        self.target_path_var = tk.StringVar(master=self)

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

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # --- UI handlers ---

    def browse_source(self):
        path = filedialog.askopenfilename(
            title="Choose source image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")],
            parent=self)
        if path:
            self.source_path_var.set(path)

    def browse_target(self):
        path = filedialog.askopenfilename(
            title="Choose target image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")],
            parent=self)
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

        if self.animation_after_id:
            self._stop_timer()

        target_w, target_h = self._fit_size_to_limit(*target.size)
        if (target_w, target_h) != target.size:
            target = target.resize((target_w, target_h), Image.LANCZOS)

        # Resize source to match target
        self.image_width, self.image_height = target_w, target_h
        source = source.resize((self.image_width, self.image_height), Image.LANCZOS)

        # Resize canvas
        canvas_w = self.image_width * 2 + self.margin * 3
        canvas_h = self.image_height + self.margin * 2
        self.canvas.config(width=canvas_w, height=canvas_h)
        self.canvas.delete("all")

        # Get blocks
        src_blocks = self.get_blocks(source)
        tgt_blocks = self.get_blocks(target)

        assignments = self.match_blocks(src_blocks, tgt_blocks)

        rnd = random.Random()
        self.pixels = []

        for src_idx, tgt_idx in assignments:
            (sx, sy), scol = src_blocks[src_idx]
            (tx, ty), _ = tgt_blocks[tgt_idx]

            start_pos = (sx + self.margin, sy + self.margin)
            target_pos = (tx + self.image_width + self.margin * 2, ty + self.margin)

            chaos = (
                target_pos[0] + rnd.randint(-self.CHAOS_SPREAD, self.CHAOS_SPREAD),
                target_pos[1] + rnd.randint(-self.CHAOS_SPREAD, self.CHAOS_SPREAD)
            )

            self.pixels.append(
                self.PixelObj(
                    current=start_pos,
                    target=target_pos,
                    chaos_target=chaos,
                    color=scol,
                    size=self.BLOCK_SIZE
                )
            )

        self.create_canvas_items()
        self.update_idletasks()

        self.start_time = time.time()
        self.animation_after_id = self.after(self.TIMER_INTERVAL_MS, self.update_animation)

    def run(self):
        # Only enter mainloop if we created our own hidden root.
        if self._owned_root is not None:
            self._owned_root.mainloop()

    def get_blocks(self, img):
        w, h = img.size
        step = self.BLOCK_SIZE
        blocks = []
        for y in range(0, h, step):
            for x in range(0, w, step):
                blocks.append(((x, y), img.getpixel((x, y))))
        return blocks

    def match_blocks(self, src_blocks, tgt_blocks):
        # Greedy nearest-color assignment: for each target block, find closest unused source color.
        count = min(len(src_blocks), len(tgt_blocks))
        src_blocks = src_blocks[:count]
        tgt_blocks = tgt_blocks[:count]

        src_colors = np.array([c for (_, c) in src_blocks], dtype=np.int16)
        tgt_colors = np.array([c for (_, c) in tgt_blocks], dtype=np.int16)

        used = np.zeros(count, dtype=bool)
        assignments = []

        for t_idx, tcol in enumerate(tgt_colors):
            available = np.where(~used)[0]
            if len(available) == 0:
                break
            diffs = src_colors[available] - tcol
            dist2 = np.einsum("ij,ij->i", diffs, diffs)
            best_local = int(available[int(np.argmin(dist2))])
            used[best_local] = True
            assignments.append((best_local, t_idx))

        return assignments

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

    # --- animation loop ---

    def update_animation(self):
        elapsed_ms = (time.time() - self.start_time) * 1000.0

        if elapsed_ms < self.INITIAL_DELAY_MS:
            self.animation_after_id = self.after(self.TIMER_INTERVAL_MS, self.update_animation)
            return

        chaos_phase_end = self.INITIAL_DELAY_MS + self.CHAOS_DURATION_MS
        all_settled = True

        for px in self.pixels:
            if elapsed_ms < chaos_phase_end:
                lerp = 0.02
                tx, ty = px.chaos_target
            else:
                lerp = 0.05
                tx, ty = px.target

            px.current[0] += (tx - px.current[0]) * lerp
            px.current[1] += (ty - px.current[1]) * lerp

            dx = abs(tx - px.current[0])
            dy = abs(ty - px.current[1])
            if dx > 0.5 or dy > 0.5:
                all_settled = False

            if px.canvas_id is not None:
                s = px.size
                self.canvas.coords(px.canvas_id, px.current[0], px.current[1], px.current[0] + s, px.current[1] + s)

        if all_settled and elapsed_ms >= chaos_phase_end:
            self._stop_timer()
            return

        self.animation_after_id = self.after(self.TIMER_INTERVAL_MS, self.update_animation)

    def _fit_size_to_limit(self, width, height):
        blocks_w = math.ceil(width / self.BLOCK_SIZE)
        blocks_h = math.ceil(height / self.BLOCK_SIZE)
        blocks = max(1, blocks_w * blocks_h)
        if blocks <= self.MAX_BLOCKS:
            return width, height

        scale = math.sqrt(self.MAX_BLOCKS / blocks)
        new_w = max(self.BLOCK_SIZE, int(width * scale))
        new_h = max(self.BLOCK_SIZE, int(height * scale))
        # keep dimensions aligned to block grid
        new_w = max(self.BLOCK_SIZE, new_w - new_w % self.BLOCK_SIZE)
        new_h = max(self.BLOCK_SIZE, new_h - new_h % self.BLOCK_SIZE)
        return new_w, new_h

    def _stop_timer(self):
        if self.animation_after_id is not None:
            self.after_cancel(self.animation_after_id)
            self.animation_after_id = None

    def _on_close(self):
        self._stop_timer()
        self.destroy()
        if self._owned_root is not None:
            self._owned_root.destroy()
            self._owned_root = None


if __name__ == "__main__":
    PixelMorphApp().run()
