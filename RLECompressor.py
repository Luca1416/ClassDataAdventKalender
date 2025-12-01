import hashlib
import tkinter as tk
from tkinter import messagebox


class RLECompressor:
    """
    Simple Run-Length Encoding (RLE) compressor / decompressor.
    """

    def encode(self, text: str) -> str:
        """
        Encode the input string using basic RLE.
        Example: 'AAABCC' -> '3A1B2C'
        """
        if not text:
            return ""

        result = []
        count = 1
        prev = text[0]

        for ch in text[1:]:
            if ch.isdigit():
                messagebox.showwarning("Warning", "No Digits allowd, output is hard to read otherwise")
                raise ValueError("Input text cannot contain digits for RLE encoding.")
            if ch == prev:
                count += 1
            else:
                result.append(f"{count}{prev}")
                prev = ch
                count = 1

        # last run
        result.append(f"{count}{prev}")
        return "".join(result)

    def decode(self, encoded: str) -> str:
        """
        Decode an RLE string back to original.
        Example: '3A1B2C' -> 'AAABCC'
        Assumes format: <count><char> repeated, where count is one or more digits.
        """
        if not encoded:
            return ""

        result = []
        count_str = ""

        for ch in encoded:
            if ch.isdigit():
                count_str += ch
            else:
                if not count_str:
                    raise ValueError("Invalid RLE format: missing count before character.")
                count = int(count_str)
                result.append(ch * count)
                count_str = ""

        if count_str:
            # trailing digits with no character
            raise ValueError("Invalid RLE format: ends with digits only.")

        return "".join(result)

    def stats(self, original: str, encoded: str) -> str:
        """
        Return a human-readable stats summary.
        """
        len_orig = len(original)
        len_comp = len(encoded)
        if len_orig == 0:
            return "Stats: empty input."

        diff = len_orig - len_comp
        ratio = len_comp / len_orig
        percent = (1 - ratio) * 100

        if diff >= 0:
            return (
                f"Stats:\n"
                f"  Original length:   {len_orig}\n"
                f"  Compressed length: {len_comp}\n"
                f"  Saved:             {diff} chars ({percent:.1f}% smaller)"
            )
        else:
            return (
                f"Stats:\n"
                f"  Original length:   {len_orig}\n"
                f"  Compressed length: {len_comp}\n"
                f"  Overhead:          {-diff} chars ({-percent:.1f}% larger)"
            )


# ---------------- UI (no extra classes) ----------------

class RLECompressorApp:
    def run(self):

        def main():
            compressor = RLECompressor()

            root = tk.Tk()
            root.title("RLE Compression Demo")
            root.geometry("900x600")

            # ---- Callbacks ----

            def do_compress():
                text = text_input.get("1.0", tk.END).rstrip("\n")
                encoded = compressor.encode(text)

                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                text_output.insert(tk.END, encoded)
                text_output.config(state="disabled")

                label_stats.config(text=compressor.stats(text, encoded))

            def do_decompress():
                encoded = text_input.get("1.0", tk.END).rstrip("\n")
                try:
                    decoded = compressor.decode(encoded)
                except ValueError as e:
                    messagebox.showerror("Decode error", str(e))
                    return

                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                text_output.insert(tk.END, decoded)
                text_output.config(state="disabled")

                # stats compared to encoded
                label_stats.config(text=compressor.stats(encoded, decoded))

            def do_clear():
                text_input.delete("1.0", tk.END)
                text_output.config(state="normal")
                text_output.delete("1.0", tk.END)
                text_output.config(state="disabled")
                label_stats.config(text="Stats: -")

            # placeholder – does nothing on purpose
            def save_program_placeholder():
                pass

            # ---- Layout ----

            # Buttons row
            frame_buttons = tk.Frame(root)
            frame_buttons.pack(padx=10, pady=10, fill="x")

            btn_compress = tk.Button(frame_buttons, text="Compress (RLE)", command=do_compress)
            btn_compress.pack(side="left")

            btn_decompress = tk.Button(frame_buttons, text="Decompress (RLE)", command=do_decompress)
            btn_decompress.pack(side="left", padx=5)

            btn_clear = tk.Button(frame_buttons, text="Clear", command=do_clear)
            btn_clear.pack(side="left", padx=5)

            btn_save = tk.Button(frame_buttons, text="Save Program", command=save_program_placeholder)
            btn_save.pack(side="left", padx=15)

            # Text areas (input / output)
            frame_text = tk.Frame(root)
            frame_text.pack(padx=10, pady=10, fill="both", expand=True)

            # Input
            frame_input = tk.LabelFrame(frame_text, text="Input")
            frame_input.pack(side="left", fill="both", expand=True, padx=(0, 5))

            text_input = tk.Text(frame_input, wrap="word")
            text_input.pack(fill="both", expand=True)

            # Output
            frame_output = tk.LabelFrame(frame_text, text="Output")
            frame_output.pack(side="left", fill="both", expand=True, padx=(5, 0))

            text_output = tk.Text(frame_output, wrap="word", state="disabled")
            text_output.pack(fill="both", expand=True)

            # Stats label
            label_stats = tk.Label(root, text="Stats: -", justify="left", anchor="w")
            label_stats.pack(padx=10, pady=(0, 10), fill="x")

            root.mainloop()

        main()


# standalone execution support
if __name__ == "__main__":
    RLECompressorApp().run()
