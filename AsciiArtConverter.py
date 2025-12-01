import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import tkinter.font as tkfont


class AsciiArtConverter:
    """
    Converts images (PNG/JPG) into ASCII art.
    """

    # From dark to light
    ASCII_CHARS = "@%#*+=-:. "

    def __init__(self, new_width: int = 80):
        self.new_width = new_width

    def set_width(self, new_width: int):
        if new_width <= 0:
            messagebox.showerror("Error", "Width must be positive.")
            return
        elif new_width > 632:
            messagebox.showerror("Error", "Width too large; max is 632.")
            return
        self.new_width = new_width

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image preserving aspect ratio.
        Height is adjusted because characters are taller than they are wide.
        """
        width, height = image.size
        aspect_ratio = height / width

        # tweak height factor so ASCII looks less squashed
        new_height = int(self.new_width * aspect_ratio * 0.55)

        return image.resize((self.new_width, max(1, new_height)))

    def _to_grayscale(self, image: Image.Image) -> Image.Image:
        return image.convert("L")  # grayscale

    def _map_pixels_to_ascii(self, image: Image.Image) -> str:
        """
        Map each pixel to an ASCII character based on brightness.
        """
        pixels = image.getdata()
        chars = []
        scale = (len(self.ASCII_CHARS) - 1) / 255

        for pixel in pixels:
            chars.append(self.ASCII_CHARS[int(pixel * scale)])

        return "".join(chars)

    def image_file_to_ascii(self, filepath: str) -> str:
        """
        Full pipeline: open image, resize, grayscale, map to ASCII, format lines.
        """
        image = Image.open(filepath)
        image = self._resize_image(image)
        image = self._to_grayscale(image)

        ascii_chars = self._map_pixels_to_ascii(image)
        # break string into lines of new_width
        lines = [
            ascii_chars[i:i + self.new_width]
            for i in range(0, len(ascii_chars), self.new_width)
        ]
        return "\n".join(lines)


# --------- UI (no additional classes) ---------

class AsciiArtConverterApp:
    def run(self):

        def main():
            converter = AsciiArtConverter(new_width=80)

            root = tk.Tk()
            root.title("Image to ASCII Converter")

            # set a default size
            root.geometry("900x600")

            # monospaced font so columns line up; size will be auto-adjusted
            ascii_font = tkfont.Font(family="Courier", size=10)

            # will store last ASCII so we can refit if needed (if you want later)
            last_ascii = {"text": ""}

            def choose_image():
                path = filedialog.askopenfilename(
                    filetypes=[
                        ("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                        ("All files", "*.*"),
                    ]
                )
                if path:
                    entry_file.delete(0, tk.END)
                    entry_file.insert(0, path)

            def auto_fit_ascii_to_box(ascii_art: str):
                """
                Shrink font size so the *longest* line fits into the text widget width.
                """
                lines = ascii_art.splitlines()
                if not lines:
                    return

                max_len = max(len(line) for line in lines)
                if max_len == 0:
                    return

                # Make sure geometry info is up to date
                root.update_idletasks()
                box_width = text_output.winfo_width()
                if box_width <= 1:
                    return  # widget not ready yet

                # Try font sizes from bigger to smaller until it fits
                max_size = 18
                min_size = 4
                best_size = min_size

                for size in range(max_size, min_size - 1, -1):
                    ascii_font.configure(size=size)
                    char_width = ascii_font.measure("M")  # monospaced, one char width
                    total_width = char_width * max_len
                    # small margin (10px)
                    if total_width <= box_width - 10:
                        best_size = size
                        break

                ascii_font.configure(size=best_size)
                text_output.configure(font=ascii_font)

            def generate_ascii():
                filepath = entry_file.get().strip()
                if not filepath:
                    messagebox.showwarning("No file", "Please select an image file first.")
                    return

                # get width from entry (optional)
                width_text = entry_width.get().strip()
                if width_text:
                    try:
                        w = int(width_text)
                        converter.set_width(w)
                    except ValueError:
                        messagebox.showerror("Error", "Width must be a positive integer.")
                        return

                try:
                    ascii_art = converter.image_file_to_ascii(filepath)
                except FileNotFoundError:
                    messagebox.showerror("Error", "File not found.")
                    return
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    return

                last_ascii["text"] = ascii_art

                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                text_output.insert(tk.END, ascii_art)
                text_output.config(state="disabled")

                auto_fit_ascii_to_box(ascii_art)

            # Zoom buttons now just call auto-fit on current ASCII
            def zoom_out():
                # re-fit font based on current box size and current ASCII
                if last_ascii["text"]:
                    auto_fit_ascii_to_box(last_ascii["text"])

            def zoom_in():
                # optional: just reset to a “normal” size
                ascii_font.configure(size=10)
                text_output.configure(font=ascii_font)

            # Blank "Save Program" button placeholder, does nothing
            def save_program_placeholder():
                pass

            # File row
            frame_file = tk.Frame(root)
            frame_file.pack(padx=10, pady=10, fill="x")

            tk.Label(frame_file, text="Image:").pack(side="left")
            entry_file = tk.Entry(frame_file)
            entry_file.pack(side="left", fill="x", expand=True, padx=5)
            tk.Button(frame_file, text="Browse...", command=choose_image).pack(side="left")

            # Width row
            frame_width = tk.Frame(root)
            frame_width.pack(padx=10, pady=5, fill="x")

            tk.Label(frame_width, text="Width (chars):").pack(side="left")
            entry_width = tk.Entry(frame_width, width=8)
            entry_width.pack(side="left", padx=5)
            entry_width.insert(0, "80")  # default

            # Buttons row
            frame_buttons = tk.Frame(root)
            frame_buttons.pack(padx=10, pady=10, fill="x")

            tk.Button(frame_buttons, text="Generate ASCII", command=generate_ascii).pack(side="left")

            tk.Button(frame_buttons, text="Refit to Box", command=zoom_out).pack(side="left", padx=5)
            tk.Button(frame_buttons, text="Reset Font", command=zoom_in).pack(side="left", padx=5)

            tk.Button(
                frame_buttons,
                text="Save Program",
                command=save_program_placeholder  # intentionally empty
            ).pack(side="left", padx=5)

            # Output
            frame_output = tk.Frame(root)
            frame_output.pack(padx=10, pady=10, fill="both", expand=True)

            text_output = tk.Text(frame_output, wrap="none", state="disabled")
            text_output.pack(fill="both", expand=True)
            text_output.configure(font=ascii_font)

            # Scrollbars (still useful if height is big)
            scroll_y = tk.Scrollbar(frame_output, orient="vertical", command=text_output.yview)
            scroll_y.pack(side="right", fill="y")
            text_output.config(yscrollcommand=scroll_y.set)

            scroll_x = tk.Scrollbar(frame_output, orient="horizontal", command=text_output.xview)
            scroll_x.pack(side="bottom", fill="x")
            text_output.config(xscrollcommand=scroll_x.set)

            root.mainloop()

        main()


# Support direct script execution
if __name__ == "__main__":
    AsciiArtConverterApp().run()
