import tkinter as tk
from tkinter import messagebox


class UnitConverterApp:
    """
    Simple unit converter with a small GUI.

    Supported units:
    - Length: m, km, cm, mm, ft, in, yd, mi
    - Weight: kg, g, mg, lb, oz
    - Temperature: C, F, K
    """

    def __init__(self):
        # Conversion factors relative to base units:
        #   length: meter (m)
        #   weight: kilogram (kg)
        self._categories = {
            "length": {
                "m": 1.0,
                "km": 1000.0,
                "cm": 0.01,
                "mm": 0.001,
                "ft": 0.3048,
                "in": 0.0254,
                "yd": 0.9144,
                "mi": 1609.344,
            },
            "weight": {
                "kg": 1.0,
                "g": 0.001,
                "mg": 0.000001,
                "lb": 0.45359237,
                "oz": 0.028349523125,
            },
        }
        self._temperature_units = {"C", "F", "K"}

        # ---- GUI setup ----
        self.root = tk.Tk()
        self.root.title("Unit Converter")

        # Value input
        tk.Label(self.root, text="Value:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.value_entry = tk.Entry(self.root, width=20)
        self.value_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="we")

        # Unit lists
        self.all_units = (
            list(self._categories["length"].keys())
            + list(self._categories["weight"].keys())
            + list(self._temperature_units)
        )
        self.all_units = sorted(set(self.all_units))

        # From unit dropdown
        tk.Label(self.root, text="From:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.from_unit_var = tk.StringVar(value="m")
        self.from_unit_menu = tk.OptionMenu(self.root, self.from_unit_var, *self.all_units)
        self.from_unit_menu.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # To unit dropdown
        tk.Label(self.root, text="To:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.to_unit_var = tk.StringVar(value="km")
        self.to_unit_menu = tk.OptionMenu(self.root, self.to_unit_var, *self.all_units)
        self.to_unit_menu.grid(row=1, column=3, padx=5, pady=5, sticky="we")

        # Convert button
        self.convert_button = tk.Button(self.root, text="Convert", command=self.on_convert)
        self.convert_button.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="we")

        # Result label
        self.result_var = tk.StringVar(value="Result will appear here")
        self.result_label = tk.Label(self.root, textvariable=self.result_var, anchor="w")
        self.result_label.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        # Make columns stretch nicely
        for col in range(4):
            self.root.grid_columnconfigure(col, weight=1)

    # ---------- Conversion logic ----------

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        from_unit = from_unit.strip()
        to_unit = to_unit.strip()

        # Temperature conversion?
        if from_unit in self._temperature_units or to_unit in self._temperature_units:
            return self._convert_temperature(value, from_unit, to_unit)

        # Find common category
        category = self._find_category(from_unit, to_unit)
        if category is None:
            raise ValueError(f"Incompatible or unknown units: '{from_unit}' -> '{to_unit}'")

        if from_unit not in self._categories[category]:
            raise ValueError(f"Unsupported from unit '{from_unit}' for category '{category}'")
        if to_unit not in self._categories[category]:
            raise ValueError(f"Unsupported to unit '{to_unit}' for category '{category}'")

        factors = self._categories[category]

        # value -> base unit -> target unit
        value_in_base = value * factors[from_unit]
        return value_in_base / factors[to_unit]

    def _find_category(self, from_unit: str, to_unit: str):
        for name, units in self._categories.items():
            if from_unit in units and to_unit in units:
                return name
        return None

    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        if from_unit not in self._temperature_units:
            raise ValueError(f"Unsupported from unit '{from_unit}' for temperature")
        if to_unit not in self._temperature_units:
            raise ValueError(f"Unsupported to unit '{to_unit}' for temperature")

        celsius = self._to_celsius(value, from_unit)
        return self._from_celsius(celsius, to_unit)

    @staticmethod
    def _to_celsius(value: float, unit: str) -> float:
        if unit == "C":
            return value
        if unit == "K":
            return value - 273.15
        if unit == "F":
            return (value - 32.0) * 5.0 / 9.0
        raise ValueError(f"Unknown temperature unit '{unit}'")

    @staticmethod
    def _from_celsius(value: float, unit: str) -> float:
        if unit == "C":
            return value
        if unit == "K":
            return value + 273.15
        if unit == "F":
            return value * 9.0 / 5.0 + 32.0
        raise ValueError(f"Unknown temperature unit '{unit}'")

    # ---------- GUI callbacks ----------

    def on_convert(self):
        raw_value = self.value_entry.get().strip()
        from_unit = self.from_unit_var.get()
        to_unit = self.to_unit_var.get()

        if not raw_value:
            messagebox.showerror("Error", "Please enter a value.")
            return

        try:
            value = float(raw_value)
        except ValueError:
            messagebox.showerror("Error", "Value must be a number.")
            return

        try:
            result = self.convert(value, from_unit, to_unit)
        except ValueError as e:
            messagebox.showerror("Conversion error", str(e))
            return

        self.result_var.set(f"{value} {from_unit} = {result:.6g} {to_unit}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = UnitConverterApp()
    app.run()
