import tkinter as tk
from tkinter import messagebox, filedialog
import random
import copy
import json


class SudokuGenerator:
    """
    Simple Sudoku board generator:
    - generate_full_board(): returns a completed 9x9 grid
    - generate_puzzle(blanks): returns a grid with some cells set to 0
    Note: does NOT guarantee unique solution (simple generator).
    """

    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def generate_full_board(self):
        """
        Generate a full valid Sudoku board using backtracking.
        """
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self._fill_board()
        return copy.deepcopy(self.board)

    def generate_puzzle(self, blanks: int = 40):
        """
        Generate a puzzle by starting from a full board and removing `blanks` cells.
        Returns the puzzle grid (with 0 as empty).
        self.board will still hold the full solution.
        """
        if blanks < 0 or blanks > 81:
            raise ValueError("Blanks must be between 0 and 81.")

        full = self.generate_full_board()   # self.board now = full solution
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)

        for i in range(blanks):
            r, c = cells[i]
            full[r][c] = 0

        # self.board is still the full solution (untouched copy from _fill_board)
        return full

    # ----- internal helpers -----

    def _fill_board(self):
        """
        Backtracking fill for a 9x9 Sudoku board.
        """
        empty = self._find_empty()
        if not empty:
            return True  # full

        row, col = empty
        nums = list(range(1, 10))
        random.shuffle(nums)

        for num in nums:
            if self._is_safe(row, col, num):
                self.board[row][col] = num
                if self._fill_board():
                    return True
                self.board[row][col] = 0

        return False

    def _find_empty(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return r, c
        return None

    def _is_safe(self, row, col, num):
        # row check
        if any(self.board[row][c] == num for c in range(9)):
            return False
        # column check
        if any(self.board[r][col] == num for r in range(9)):
            return False
        # 3x3 box check
        box_row = (row // 3) * 3
        box_col = (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if self.board[r][c] == num:
                    return False
        return True


# ---------------- UI (no extra classes) ----------------

class SudokuApp:
    def __init__(self):
        self.generator = SudokuGenerator()

    def run(self):
        generator = self.generator

        root = tk.Tk()
        root.title("Sudoku Board Generator (Simple)")
        root.resizable(False, False)

        # 9x9 grid of Entry widgets
        entries = [[None for _ in range(9)] for _ in range(9)]

        # store solution & puzzle for validation/export
        solution_board = {"grid": None}
        puzzle_board = {"grid": None}

        def display_full_board(board):
            """
            Show a completed board; all cells black + disabled.
            """
            for r in range(9):
                for c in range(9):
                    val = board[r][c]
                    e = entries[r][c]
                    e.config(state="normal", fg="black")
                    e.delete(0, tk.END)
                    if val != 0:
                        e.insert(0, str(val))
                    e.config(state="disabled")

        def display_puzzle(board):
            """
            Show a puzzle:
            - given clues: black, disabled
            - empty cells (0): enabled, blue; user can type.
            """
            for r in range(9):
                for c in range(9):
                    val = board[r][c]
                    e = entries[r][c]
                    e.config(state="normal")
                    e.delete(0, tk.END)
                    if val != 0:
                        e.insert(0, str(val))
                        e.config(fg="black", state="disabled")  # clues locked
                    else:
                        # user can type here; start as blue (unvalidated)
                        e.config(fg="blue", state="normal")

        def generate_full():
            board = generator.generate_full_board()
            solution_board["grid"] = copy.deepcopy(board)
            puzzle_board["grid"] = None
            display_full_board(board)

        def generate_puzzle():
            blanks_text = entry_blanks.get().strip()
            if not blanks_text:
                blanks = 40  # default
            else:
                try:
                    blanks = int(blanks_text)
                except ValueError:
                    messagebox.showerror("Error", "Blanks must be a whole number.")
                    return

            try:
                board = generator.generate_puzzle(blanks=blanks)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return

            # generator.board still holds the full solution
            solution_board["grid"] = copy.deepcopy(generator.board)
            puzzle_board["grid"] = copy.deepcopy(board)

            display_puzzle(board)

        def validate_user_input():
            """
            Check user input against solution.
            - Only user cells (where puzzle had 0) are checked.
            - Correct entries -> green
            - Wrong/invalid entries -> red
            - Empty entries stay blue
            """
            if solution_board["grid"] is None or puzzle_board["grid"] is None:
                messagebox.showwarning("No puzzle", "Please generate a puzzle first.")
                return

            solution = solution_board["grid"]
            puzzle = puzzle_board["grid"]

            any_error = False
            any_missing = False

            for r in range(9):
                for c in range(9):
                    clue_val = puzzle[r][c]
                    sol_val = solution[r][c]
                    e = entries[r][c]

                    if clue_val != 0:
                        # given clue, keep as black
                        e.config(fg="black")
                        continue

                    # user-editable cell
                    text = e.get().strip()

                    if text == "":
                        # empty: still missing
                        e.config(fg="blue")
                        any_missing = True
                        continue

                    if not (len(text) == 1 and text.isdigit() and text != "0"):
                        # invalid input
                        e.config(fg="red")
                        any_error = True
                        continue

                    val = int(text)
                    if val == sol_val:
                        # correct -> green
                        e.config(fg="green")
                    else:
                        # incorrect -> red
                        e.config(fg="red")
                        any_error = True

            if any_error:
                messagebox.showinfo("Validation", "There are incorrect entries (marked in red).")
            elif any_missing:
                messagebox.showinfo("Validation", "All filled numbers are correct so far, but some cells are still empty.")
            else:
                messagebox.showinfo("Validation", "All numbers are correct – Sudoku solved!")

        def export_to_json():
            """
            Export only the CURRENT BOARD (what the user sees) as JSON:
            {
            "board": [[...],[...],...]
            }
            """
            if solution_board["grid"] is None and puzzle_board["grid"] is None:
                messagebox.showwarning("No data", "Generate a full board or puzzle first.")
                return

            board = [[0 for _ in range(9)] for _ in range(9)]
            for r in range(9):
                for c in range(9):
                    txt = entries[r][c].get().strip()
                    if len(txt) == 1 and txt.isdigit():
                        board[r][c] = int(txt)
                    else:
                        board[r][c] = 0

            data = {"board": board}

            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Board as JSON"
            )
            if not path:
                return

            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Export", f"Board exported to:\n{path}")
            except Exception as e:
                messagebox.showerror("Export error", str(e))

        def save_program_placeholder():
            pass

        frame_grid = tk.Frame(root, padx=10, pady=10)
        frame_grid.pack()

        for r in range(9):
            for c in range(9):
                e = tk.Entry(frame_grid, width=2, justify="center", font=("Arial", 14))
                bd_top = 2 if r % 3 == 0 else 1
                bd_left = 2 if c % 3 == 0 else 1
                e.grid(row=r, column=c, padx=(bd_left, 1), pady=(bd_top, 1))
                e.config(state="disabled")
                entries[r][c] = e

        frame_controls = tk.Frame(root, padx=10, pady=10)
        frame_controls.pack(fill="x")

        btn_full = tk.Button(frame_controls, text="Generate Full Board", command=generate_full)
        btn_full.pack(side="left")

        tk.Label(frame_controls, text="Blanks:").pack(side="left", padx=(10, 0))
        entry_blanks = tk.Entry(frame_controls, width=5)
        entry_blanks.pack(side="left")
        entry_blanks.insert(0, "40")

        btn_puzzle = tk.Button(frame_controls, text="Generate Puzzle", command=generate_puzzle)
        btn_puzzle.pack(side="left", padx=5)

        btn_validate = tk.Button(frame_controls, text="Validate", command=validate_user_input)
        btn_validate.pack(side="left", padx=5)

        btn_export = tk.Button(frame_controls, text="Export JSON", command=export_to_json)
        btn_export.pack(side="left", padx=5)

        btn_save = tk.Button(frame_controls, text="Save Program", command=save_program_placeholder)
        btn_save.pack(side="left", padx=15)

        root.mainloop()


# For direct script running
if __name__ == "__main__":
    SudokuApp().run()
