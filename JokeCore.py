import tkinter as tk
from tkinter import messagebox, ttk, filedialog

class JokeCore:
    def __init__(self, jokePart1: str, jokePart2: str = ""):
        self.jokePart1 = jokePart1
        self.jokePart2 = jokePart2
        self.root = tk.Tk()
        self.root.withdraw()

    def showJoke(self, part: int = 0):
        root2 = tk.Toplevel(self.root)
        root2.geometry("250x120")
        root2.title("Flachwitz" if part == 0 else "haha")

        
        if self.jokePart2 != "":
            text = self.jokePart1 if part == 1 else self.jokePart2
        else:
            text = self.jokePart1
        
        text = "Ready for todays joke?" if part == 0 else text
        label = tk.Label(root2, text = text)
        label.pack(pady=10)
        def whyTF():
            root2.destroy()
            self.showJoke(1)if part == 0 else self.showJoke(2) if part == 1 else None
        button = tk.Button(root2, text="Ok", command=whyTF)
        button.pack(pady=5)