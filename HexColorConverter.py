import tkinter as tk
from tkinter import messagebox


class HexColorConverter:
    """
    Simple converter between RGB tuples and Hex color codes.
    """

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        if not all(0 <= x <= 255 for x in (r, g, b)):
            raise ValueError("RGB values must be between 0 and 255.")
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    @staticmethod
    def hex_to_rgb(hexcode: str):
        hexcode = hexcode.strip().lstrip("#")
        if len(hexcode) != 6:
            raise ValueError("Hex code must be 6 characters.")
        try:
            r = int(hexcode[0:2], 16)
            g = int(hexcode[2:4], 16)
            b = int(hexcode[4:6], 16)
        except ValueError:
            raise ValueError("Invalid hex characters.")
        return r, g, b


# ---------------- UI (no classes below) ----------------

class HexColorConverterApp:
    def run(self):

        def hexConvert():
            converter = HexColorConverter()

            def convert_to_hex():
                try:
                    r = int(entry_r.get())
                    g = int(entry_g.get())
                    b = int(entry_b.get())
                    result = converter.rgb_to_hex(r, g, b)
                    output_color(result)
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            def convert_to_rgb():
                try:
                    rgb = converter.hex_to_rgb(entry_hex.get())
                    result_text.config(state="normal")
                    result_text.delete("1.0", tk.END)
                    result_text.insert(tk.END, f"RGB: {rgb}")
                    result_text.config(state="disabled")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            def output_color(hexcode):
                result_text.config(state="normal")
                result_text.delete("1.0", tk.END)
                result_text.insert(tk.END, f"Hex: {hexcode}")
                result_text.config(state="disabled")

            # Blank button function (intentionally empty)
            def save_program_placeholder():
                pass

            # ----- Build UI -----

            root = tk.Tk()
            root.title("Hex Color Converter")

            # RGB → HEX
            frame_rgb = tk.LabelFrame(root, text="RGB to HEX")
            frame_rgb.pack(padx=10, pady=10, fill="x")

            tk.Label(frame_rgb, text="R:").grid(row=0, column=0)
            tk.Label(frame_rgb, text="G:").grid(row=0, column=2)
            tk.Label(frame_rgb, text="B:").grid(row=0, column=4)

            entry_r = tk.Entry(frame_rgb, width=4)
            entry_g = tk.Entry(frame_rgb, width=4)
            entry_b = tk.Entry(frame_rgb, width=4)

            entry_r.grid(row=0, column=1, padx=5)
            entry_g.grid(row=0, column=3, padx=5)
            entry_b.grid(row=0, column=5, padx=5)

            btn_rgb_to_hex = tk.Button(frame_rgb, text="Convert to Hex", command=convert_to_hex)
            btn_rgb_to_hex.grid(row=1, column=0, columnspan=6, pady=5)

            # HEX → RGB
            frame_hex = tk.LabelFrame(root, text="HEX to RGB")
            frame_hex.pack(padx=10, pady=10, fill="x")

            tk.Label(frame_hex, text="Hex (#RRGGBB):").grid(row=0, column=0)
            entry_hex = tk.Entry(frame_hex)
            entry_hex.grid(row=0, column=1, padx=5)

            btn_hex_to_rgb = tk.Button(frame_hex, text="Convert to RGB", command=convert_to_rgb)
            btn_hex_to_rgb.grid(row=1, column=0, columnspan=2, pady=5)

            # Result display
            frame_result = tk.Frame(root)
            frame_result.pack(padx=10, pady=10, fill="both", expand=True)

            result_text = tk.Text(frame_result, height=3, state="disabled")
            result_text.pack(fill="both", expand=True)

            # Save Program (blank)
            btn_save = tk.Button(root, text="Save Program", command=save_program_placeholder)
            btn_save.pack(pady=5)

            root.mainloop()

        hexConvert()


# Allow standalone script running
if __name__ == "__main__":
    HexColorConverterApp().run()
