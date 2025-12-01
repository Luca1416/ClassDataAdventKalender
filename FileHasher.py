import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox


class FileHasher:
    """
    Simple file hash generator supporting MD5 and SHA256.
    """

    def __init__(self, chunk_size: int = 8192):
        self.chunk_size = chunk_size

    def hash_file(self, filepath: str, algorithm: str = "md5") -> str:
        """
        Compute the hash of a file using the given algorithm ("md5" or "sha256").
        """
        algorithm = algorithm.lower()
        if algorithm == "md5":
            hasher = hashlib.md5()
        elif algorithm == "sha256":
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        return hasher.hexdigest()


# --- UI code (no extra classes) ---

class FileHasherApp:
    def run(self):

        def hasher():
            hasher = FileHasher()

            def choose_file():
                path = filedialog.askopenfilename()
                if path:
                    entry_file.delete(0, tk.END)
                    entry_file.insert(0, path)

            def compute_hash():
                filepath = entry_file.get().strip()
                if not filepath:
                    messagebox.showwarning("No file", "Please select a file first.")
                    return

                algorithm = algo_var.get()
                try:
                    digest = hasher.hash_file(filepath, algorithm)
                except FileNotFoundError:
                    messagebox.showerror("Error", "File not found.")
                    return
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    return

                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                text_output.insert(tk.END, f"{algorithm.upper()} hash:\n{digest}")
                text_output.config(state="disabled")

            # Blank handler for the "Save Program" button (intentionally does nothing)
            # You asked for this to be blank and not class-based.
            def save_program_placeholder():
                # Intentionally left empty
                # (no functionality wired up yet)
                pass

            # --- Build UI ---

            root = tk.Tk()
            root.title("File Hash Generator (MD5 / SHA256)")

            # File selection row
            frame_file = tk.Frame(root)
            frame_file.pack(padx=10, pady=10, fill="x")

            label_file = tk.Label(frame_file, text="File:")
            label_file.pack(side="left")

            entry_file = tk.Entry(frame_file)
            entry_file.pack(side="left", fill="x", expand=True, padx=5)

            btn_browse = tk.Button(frame_file, text="Browse...", command=choose_file)
            btn_browse.pack(side="left")

            # Algorithm selection
            frame_algo = tk.Frame(root)
            frame_algo.pack(padx=10, pady=5, fill="x")

            algo_var = tk.StringVar(value="md5")

            label_algo = tk.Label(frame_algo, text="Algorithm:")
            label_algo.pack(side="left")

            radio_md5 = tk.Radiobutton(frame_algo, text="MD5", variable=algo_var, value="md5")
            radio_md5.pack(side="left", padx=5)

            radio_sha256 = tk.Radiobutton(frame_algo, text="SHA256", variable=algo_var, value="sha256")
            radio_sha256.pack(side="left", padx=5)

            # Buttons row (Compute + Save Program)
            frame_buttons = tk.Frame(root)
            frame_buttons.pack(padx=10, pady=10, fill="x")

            btn_compute = tk.Button(frame_buttons, text="Compute Hash", command=compute_hash)
            btn_compute.pack(side="left")

            # "Save Program" button – currently blank / placeholder
            btn_save_program = tk.Button(
                frame_buttons,
                text="Save Program",
                command=save_program_placeholder  # does nothing for now
            )
            btn_save_program.pack(side="left", padx=5)

            # Output area
            frame_output = tk.Frame(root)
            frame_output.pack(padx=10, pady=10, fill="both", expand=True)

            text_output = tk.Text(frame_output, height=5, wrap="word", state="disabled")
            text_output.pack(fill="both", expand=True)

            root.mainloop()

        hasher()


# allow standalone script running
if __name__ == "__main__":
    FileHasherApp().run()
