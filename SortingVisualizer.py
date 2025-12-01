import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont
import random


class SortingVisualizer:
    """
    Generates data, records sorting steps, and renders ASCII bar states.
    """

    def __init__(self):
        self.data = []

    def generate_data(self, length: int, min_val: int = 1, max_val: int = 100):
        if length <= 0:
            raise ValueError("Length must be positive.")
        if length > 100:
            raise ValueError("Length too large; max is 100 for readability.")
        self.data = [random.randint(min_val, max_val) for _ in range(length)]

    # ---- Sorting algorithms: yield states (data snapshot, highlight_indices) ----

    def bubble_sort_steps(self):
        arr = self.data.copy()
        n = len(arr)
        # initial state
        yield arr.copy(), (-1, -1)
        for i in range(n):
            for j in range(0, n - i - 1):
                # state: comparing j and j+1
                yield arr.copy(), (j, j + 1)
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    # state after swap
                    yield arr.copy(), (j, j + 1)
        # final state
        yield arr.copy(), (-1, -1)

    def insertion_sort_steps(self):
        arr = self.data.copy()
        n = len(arr)
        yield arr.copy(), (-1, -1)
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            # highlight current key
            yield arr.copy(), (i, j)
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
                yield arr.copy(), (j, j + 1)
            arr[j + 1] = key
            yield arr.copy(), (j + 1, i)
        yield arr.copy(), (-1, -1)

    def selection_sort_steps(self):
        arr = self.data.copy()
        n = len(arr)
        yield arr.copy(), (-1, -1)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                yield arr.copy(), (min_idx, j)
                if arr[j] < arr[min_idx]:
                    min_idx = j
                    yield arr.copy(), (min_idx, j)
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            yield arr.copy(), (i, min_idx)
        yield arr.copy(), (-1, -1)

    def get_steps(self, algorithm: str):
        if algorithm == "Bubble Sort":
            return list(self.bubble_sort_steps())
        elif algorithm == "Insertion Sort":
            return list(self.insertion_sort_steps())
        elif algorithm == "Selection Sort":
            return list(self.selection_sort_steps())
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    # ---- ASCII rendering ----

    def render_ascii(self, data, highlight_indices=()):
        """
        Render the list of numbers as horizontal ASCII bars.
        Highlight two indices (if provided) with a '>' marker.
        """
        if not data:
            return "(no data)"

        max_val = max(data)
        lines = []
        hi_set = set(idx for idx in highlight_indices if 0 <= idx < len(data))

        # scale bars to max width (30 chars)
        max_bar_width = 30
        scale = max_bar_width / max_val if max_val > 0 else 1

        for idx, val in enumerate(data):
            bar_len = max(1, int(val * scale))
            bar = "#" * bar_len
            prefix = "> " if idx in hi_set else "  "
            lines.append(f"{prefix}{val:3d}: {bar}")

        return "\n".join(lines)


# ---------------- UI (no extra classes) ----------------

class SortingVisualizerApp:
    def run(self):

        def main():
            visualizer = SortingVisualizer()

            root = tk.Tk()
            root.title("Sorting Algorithm Visualizer (ASCII)")
            root.geometry("900x600")

            ascii_font = tkfont.Font(family="Courier", size=10)

            current_steps = []
            current_index = {"value": 0}
            is_playing = {"value": False}
            delay_ms = {"value": 150}

            # ---- UI callbacks ----

            def generate_data():
                length_text = entry_length.get().strip()
                if not length_text:
                    messagebox.showwarning("No length", "Please enter the list length.")
                    return
                try:
                    length = int(length_text)
                except ValueError:
                    messagebox.showerror("Error", "Length must be a whole number.")
                    return

                try:
                    visualizer.generate_data(length)
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return

                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                ascii_state = visualizer.render_ascii(visualizer.data)
                text_output.insert(tk.END, ascii_state)
                text_output.config(state="disabled")

                current_steps.clear()
                current_index["value"] = 0
                is_playing["value"] = False

            def prepare_steps():
                algo = algo_var.get()
                if not visualizer.data:
                    messagebox.showwarning("No data", "Generate data first.")
                    return

                try:
                    steps = visualizer.get_steps(algo)
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return

                current_steps.clear()
                current_steps.extend(steps)
                current_index["value"] = 0
                is_playing["value"] = False

                show_current_step()

            def show_current_step():
                if not current_steps:
                    return
                idx = current_index["value"]
                idx = max(0, min(idx, len(current_steps) - 1))
                current_index["value"] = idx
                data, hi = current_steps[idx]
                ascii_state = visualizer.render_ascii(data, hi)

                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                text_output.insert(tk.END, ascii_state)
                text_output.config(state="disabled")

                label_step.config(text=f"Step: {idx + 1} / {len(current_steps)}")

            def next_step():
                if not current_steps:
                    prepare_steps()
                    if not current_steps:
                        return
                if current_index["value"] < len(current_steps) - 1:
                    current_index["value"] += 1
                    show_current_step()

            def prev_step():
                if not current_steps:
                    prepare_steps()
                    if not current_steps:
                        return
                if current_index["value"] > 0:
                    current_index["value"] -= 1
                    show_current_step()

            def play_animation():
                if not current_steps:
                    prepare_steps()
                    if not current_steps:
                        return
                is_playing["value"] = True

                def step_play():
                    if not is_playing["value"]:
                        return
                    if current_index["value"] < len(current_steps) - 1:
                        current_index["value"] += 1
                        show_current_step()
                        root.after(delay_ms["value"], step_play)
                    else:
                        is_playing["value"] = False

                step_play()

            def stop_animation():
                is_playing["value"] = False

            def update_delay(*_args):
                text_val = entry_delay.get().strip()
                try:
                    ms = int(text_val)
                    if ms <= 0:
                        return  # ignore until valid
                    delay_ms["value"] = ms
                except:
                    pass  # don't error while typing


            def save_program_placeholder():
                # intentionally does nothing
                pass

            # ---- Layout ----

            # Top frame: controls
            frame_top = tk.Frame(root)
            frame_top.pack(padx=10, pady=10, fill="x")

            # length entry
            tk.Label(frame_top, text="Length:").grid(row=0, column=0, sticky="w")
            entry_length = tk.Entry(frame_top, width=6)
            entry_length.grid(row=0, column=1, padx=5)
            entry_length.insert(0, "15")

            btn_generate = tk.Button(frame_top, text="Generate Data", command=generate_data)
            btn_generate.grid(row=0, column=2, padx=5)

            # algorithm choice
            tk.Label(frame_top, text="Algorithm:").grid(row=0, column=3, padx=(20, 0), sticky="w")
            algo_var = tk.StringVar(value="Bubble Sort")
            combo_algo = tk.OptionMenu(frame_top, algo_var, "Bubble Sort", "Insertion Sort", "Selection Sort")
            combo_algo.grid(row=0, column=4, padx=5)

            btn_prepare = tk.Button(frame_top, text="Prepare Steps", command=prepare_steps)
            btn_prepare.grid(row=0, column=5, padx=5)

            # delay
            tk.Label(frame_top, text="Delay (ms):").grid(row=1, column=0, sticky="w", pady=(8, 0))
            entry_delay = tk.Entry(frame_top, width=6)
            entry_delay.grid(row=1, column=1, padx=5, pady=(8, 0))
            entry_delay.insert(0, str(delay_ms["value"]))
            entry_delay.bind("<KeyRelease>", update_delay)

            # playback buttons
            btn_prev = tk.Button(frame_top, text="Prev", command=prev_step)
            btn_prev.grid(row=1, column=2, padx=5, pady=(8, 0))

            btn_next = tk.Button(frame_top, text="Next", command=next_step)
            btn_next.grid(row=1, column=3, padx=5, pady=(8, 0))

            btn_play = tk.Button(frame_top, text="Play", command=play_animation)
            btn_play.grid(row=1, column=4, padx=5, pady=(8, 0))

            btn_stop = tk.Button(frame_top, text="Stop", command=stop_animation)
            btn_stop.grid(row=1, column=5, padx=5, pady=(8, 0))

            # Save Program button (blank)
            btn_save_program = tk.Button(frame_top, text="Save Program", command=save_program_placeholder)
            btn_save_program.grid(row=1, column=6, padx=15, pady=(8, 0))

            # Step label
            label_step = tk.Label(root, text="Step: - / -")
            label_step.pack(pady=(0, 5))

            # Output text area
            frame_output = tk.Frame(root)
            frame_output.pack(padx=10, pady=10, fill="both", expand=True)

            text_output = tk.Text(frame_output, wrap="none", state="disabled")
            text_output.pack(side="left", fill="both", expand=True)
            text_output.configure(font=ascii_font)

            scroll_y = tk.Scrollbar(frame_output, orient="vertical", command=text_output.yview)
            scroll_y.pack(side="right", fill="y")
            text_output.config(yscrollcommand=scroll_y.set)

            scroll_x = tk.Scrollbar(root, orient="horizontal", command=text_output.xview)
            scroll_x.pack(fill="x")
            text_output.config(xscrollcommand=scroll_x.set)

            root.mainloop()

        main()


if __name__ == "__main__":
    SortingVisualizerApp().run()
