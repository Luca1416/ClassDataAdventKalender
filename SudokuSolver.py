import tkinter as tk
from tkinter import messagebox, filedialog
import json
import copy


class SudokuSolver:
    """
    Simple 9x9 Sudoku solver using backtracking.

    Expects a board as a 9x9 list of lists with 0 for empty cells.
    """

    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def load_board(self, board):
        """
        Load a 9x9 board (0 = empty).
        Raises ValueError on invalid format.
        """
        if not isinstance(board, list) or len(board) != 9:
            raise ValueError("Board must be a list of 9 rows.")
        for row in board:
            if not isinstance(row, list) or len(row) != 9:
                raise ValueError("Each row must be a list of 9 integers.")
            for val in row:
                if not isinstance(val, int) or not (0 <= val <= 9):
                    raise ValueError("Cells must be integers between 0 and 9.")
        self.board = copy.deepcopy(board)

    def solve(self):
        """
        Solve the Sudoku in-place.
        Returns True if solvable, False otherwise.
        """
        empty = self._find_empty()
        if not empty:
            return True

        row, col = empty
        for num in range(1, 10):
            if self._is_safe(row, col, num):
                self.board[row][col] = num
                if self.solve():
                    return True
                self.board[row][col] = 0
        return False

    def get_board(self):
        return copy.deepcopy(self.board)

    # ---- internal helpers ----

    def _find_empty(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return r, c
        return None

    def _is_safe(self, row, col, num):
        # row
        if any(self.board[row][c] == num for c in range(9)):
            return False
        # col
        if any(self.board[r][col] == num for r in range(9)):
            return False
        # box
        br = (row // 3) * 3
        bc = (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if self.board[r][c] == num:
                    return False
        return True


# ---------------- UI (no extra classes) ----------------

class SudokuSolverApp:
    def run(self):

        def main():
            solver = SudokuSolver()

            root = tk.Tk()
            root.title("Sudoku Solver (JSON Import)")
            root.resizable(False, False)

            entries = [[None for _ in range(9)] for _ in range(9)]
            original_board = {"grid": None}  # to know which cells are given

            def clear_grid():
                for r in range(9):
                    for c in range(9):
                        e = entries[r][c]
                        e.config(state="normal", fg="black")
                        e.delete(0, tk.END)
                        e.config(state="disabled")

            def display_board(board, original=None):
                """
                Show a solved board.
                original: original board (to color givens black, added numbers green).
                If original is None, all numbers are black.
                """
                for r in range(9):
                    for c in range(9):
                        val = board[r][c]
                        e = entries[r][c]

                        # decide color first
                        if original is not None and original[r][c] == 0 and val != 0:
                            # this cell was empty before → solver filled it
                            color = "green"
                        else:
                            color = "black"

                        e.config(state="normal")
                        e.delete(0, tk.END)

                        if val != 0:
                            e.insert(0, str(val))
                        # apply both fg and disabledforeground so it stays colored when disabled
                        e.config(fg=color, disabledforeground=color)

                        e.config(state="disabled")

            def import_json():
                path = filedialog.askopenfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    title="Import Sudoku JSON"
                )
                if not path:
                    return

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    messagebox.showerror("Import error", f"Could not read file:\n{e}")
                    return

                if "board" not in data:
                    messagebox.showerror("Format error", "JSON must contain a 'board' field.")
                    return

                try:
                    board = data["board"]
                    solver.load_board(board)
                except ValueError as e:
                    messagebox.showerror("Format error", str(e))
                    return

                original_board["grid"] = copy.deepcopy(board)
                display_board(board, original=None)

            def solve_sudoku():
                if original_board["grid"] is None:
                    messagebox.showwarning("No board", "Please import a JSON board first.")
                    return

                # load original board into solver again
                try:
                    solver.load_board(original_board["grid"])
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return

                if not solver.solve():
                    messagebox.showinfo("Unsolvable", "This Sudoku has no solution.")
                    return

                solved = solver.get_board()
                display_board(solved, original_board["grid"])

            # Save Program placeholder (does nothing)
            def save_program_placeholder():
                pass

            # ---- layout ----
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

            btn_import = tk.Button(frame_controls, text="Import JSON Board", command=import_json)
            btn_import.pack(side="left")

            btn_solve = tk.Button(frame_controls, text="Solve", command=solve_sudoku)
            btn_solve.pack(side="left", padx=5)

            btn_clear = tk.Button(frame_controls, text="Clear", command=clear_grid)
            btn_clear.pack(side="left", padx=5)

            btn_save = tk.Button(frame_controls, text="Save Program", command=save_program_placeholder)
            btn_save.pack(side="left", padx=15)

            root.mainloop()

        main()


# allow standalone running unchanged
if __name__ == "__main__":
    SudokuSolverApp().run()
