#!/usr/bin/env python3
import os
import sys
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class HashSearchApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Finder by Hash")
        self.geometry("800x500")

        self.search_thread = None
        self.stop_flag = False

        self.create_widgets()

    # ---------------- UI SETUP ----------------
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Hash input
        hash_frame = ttk.LabelFrame(main_frame, text="Hash")
        hash_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(hash_frame, text="MD5 / SHA256:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hash_entry = ttk.Entry(hash_frame)
        self.hash_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        hash_frame.columnconfigure(1, weight=1)

        # Algorithm selection
        algo_frame = ttk.LabelFrame(main_frame, text="Algorithm")
        algo_frame.pack(fill=tk.X, pady=(0, 10))

        self.algo_var = tk.StringVar(value="auto")
        ttk.Radiobutton(algo_frame, text="Auto (base on length)", variable=self.algo_var, value="auto").grid(
            row=0, column=0, sticky="w", padx=5, pady=2
        )
        ttk.Radiobutton(algo_frame, text="MD5", variable=self.algo_var, value="md5").grid(
            row=0, column=1, sticky="w", padx=5, pady=2
        )
        ttk.Radiobutton(algo_frame, text="SHA256", variable=self.algo_var, value="sha256").grid(
            row=0, column=2, sticky="w", padx=5, pady=2
        )

        # Start directory
        dir_frame = ttk.LabelFrame(main_frame, text="Search Location")
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(dir_frame, text="Start folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        dir_frame.columnconfigure(1, weight=1)

        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_directory)
        browse_btn.grid(row=0, column=2, sticky="e", padx=5, pady=5)

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.first_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Stop after first match",
            variable=self.first_only_var
        ).pack(side=tk.LEFT, padx=5)

        # Buttons (start/stop)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = ttk.Button(btn_frame, text="Start Search", command=self.on_start_search)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.on_stop_search, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Status
        self.status_var = tk.StringVar(value="Ready.")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=(0, 5))

        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Log / Results")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(results_frame, wrap="none")
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scrollbar_y.set)

    # ---------------- HELPERS ----------------
    def log(self, msg):
        """Thread-safe logging into the text box."""
        def write():
            self.text.insert(tk.END, msg + "\n")
            self.text.see(tk.END)

        self.after(0, write)

    def set_status(self, msg):
        self.after(0, lambda: self.status_var.set(msg))

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def detect_algorithm(self, hash_str):
        h = hash_str.lower()
        if len(h) == 32:
            return "md5"
        elif len(h) == 64:
            return "sha256"
        else:
            raise ValueError("Cannot auto-detect algorithm from hash length. Please choose MD5 or SHA256 manually.")

    def hash_file(self, path, algo, chunk_size=1024 * 1024):
        try:
            if algo == "md5":
                h = hashlib.md5()
            elif algo == "sha256":
                h = hashlib.sha256()
            else:
                raise ValueError(f"Unsupported algorithm: {algo}")

            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()
        except (PermissionError, FileNotFoundError, OSError):
            return None

    # ---------------- SEARCH LOGIC ----------------
    def on_start_search(self):
        if self.search_thread and self.search_thread.is_alive():
            messagebox.showinfo("Search running", "A search is already running.")
            return

        hash_value = self.hash_entry.get().strip().lower()
        start_dir = self.dir_entry.get().strip() or "."

        if not hash_value:
            messagebox.showerror("Error", "Please enter a hash value.")
            return

        algo_mode = self.algo_var.get()
        if algo_mode == "auto":
            try:
                algo = self.detect_algorithm(hash_value)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
        else:
            algo = algo_mode

        if not os.path.isdir(start_dir):
            messagebox.showerror("Error", f"Start folder does not exist:\n{start_dir}")
            return

        # Clear log
        self.text.delete(1.0, tk.END)

        self.stop_flag = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.log(f"[*] Using algorithm: {algo}")
        self.log(f"[*] Target hash:    {hash_value}")
        self.log(f"[*] Scanning from:  {os.path.abspath(start_dir)}")
        self.log("")

        self.set_status("Scanning...")

        self.search_thread = threading.Thread(
            target=self.run_search,
            args=(hash_value, start_dir, algo, self.first_only_var.get()),
            daemon=True,
        )
        self.search_thread.start()

    def on_stop_search(self):
        if self.search_thread and self.search_thread.is_alive():
            self.stop_flag = True
            self.set_status("Stopping...")

    def run_search(self, target_hash, start_dir, algo, stop_first):
        matches = []
        target_hash = target_hash.lower()

        try:
            for root, dirs, files in os.walk(start_dir):
                if self.stop_flag:
                    self.log("[*] Search stopped by user.")
                    break

                for name in files:
                    if self.stop_flag:
                        break

                    full_path = os.path.join(root, name)
                    self.log(f"Scanning: {full_path}")
                    digest = self.hash_file(full_path, algo)
                    if digest is None:
                        continue
                    if digest.lower() == target_hash:
                        self.log(f"[+] MATCH: {full_path}")
                        matches.append(full_path)
                        if stop_first:
                            self.log("[*] Stopping after first match (option enabled).")
                            self.stop_flag = True
                            break
        except Exception as e:
            self.log(f"[!] Error: {e}")
        finally:
            # Update buttons and status when done
            def on_done():
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                if self.stop_flag and not matches:
                    self.set_status("Stopped.")
                elif matches:
                    self.set_status(f"Done. Found {len(matches)} match(es).")
                else:
                    self.set_status("Done. No matches found.")

            self.after(0, on_done)


def main():
    app = HashSearchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
