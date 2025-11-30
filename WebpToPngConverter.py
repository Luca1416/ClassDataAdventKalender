# Requires: pip install pillow

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import shutil

class WebpToPngConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WEBP → PNG Converter")
        self.root.geometry("300x130")

        tk.Button(self.root, text="Select WEBP and Convert",
                  command=self.convert).pack(pady=10)

        tk.Button(self.root, text="Save Programm",
                  command=self.save_program).pack(pady=5)

    def convert(self):
        path = filedialog.askopenfilename(
            title="Select WEBP",
            filetypes=[("WEBP images", "*.webp")]
        )
        if not path:
            return

        try:
            img = Image.open(path)
            save_path = path.rsplit(".", 1)[0] + ".png"
            img.save(save_path, "PNG")
            messagebox.showinfo("Done", f"Saved:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_program(self):
        try:
            # path of the currently running .py file
            current_file = os.path.abspath(__file__)

            # user’s Downloads folder
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")

            # create target path
            target_path = os.path.join(downloads, os.path.basename(current_file))

            shutil.copy(current_file, target_path)
            messagebox.showinfo("Saved", f"Programm saved to:\n{target_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    WebpToPngConverter().run()
