import tkinter as tk


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.not_fishing = True
        self.title("Auto Fish")
        # Create a label for the fish type
        type_label = tk.Label(self, text="Select a fish type:")
        type_label.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky=tk.W)

        # Create a radio button group for the fish type
        self.type_var = tk.StringVar()
        self.type_var.set("yellow")
        type_rb1 = tk.Radiobutton(self, text="White", variable=self.type_var, value="white")
        type_rb2 = tk.Radiobutton(self, text="Blue", variable=self.type_var, value="blue")
        type_rb3 = tk.Radiobutton(self, text="Yellow", variable=self.type_var, value="yellow")
        type_rb1.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        type_rb2.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        type_rb3.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)

        # Create a label for the location
        loc_label = tk.Label(self, text="Select a location:")
        loc_label.grid(row=2, column=0, padx=10, pady=10, columnspan=3, sticky=tk.W)

        # Create a radio button group for the location
        self.loc_var = tk.StringVar()
        self.loc_var.set("bilefen")
        loc_rb1 = tk.Radiobutton(self, text="Bilefen 苦沼岛", variable=self.loc_var, value="bilefen")
        loc_rb2 = tk.Radiobutton(self, text="Ashwold 灰陵墓园", variable=self.loc_var, value="ashwold")
        loc_rb3 = tk.Radiobutton(self, text="Tundra 冰冻苔原", variable=self.loc_var, value="tundra")
        loc_rb1.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        loc_rb2.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        loc_rb3.grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)

        # auto salvage settings
        self.auto_salv_var = tk.BooleanVar()
        self.auto_salv_var.set(True)
        self.salv_capacity_var = tk.IntVar()
        self.salv_capacity_var.set(20)
        auto_salvage_label = tk.Label(self, text="Auto Salvage Settings:")
        auto_salvage_label.grid(row=4, column=0, padx=10, pady=10, columnspan=3, sticky=tk.W)
        auto_salvage_checkbtn = tk.Checkbutton(self, text="Auto Salvage", variable=self.auto_salv_var)
        auto_salvage_checkbtn.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        salvage_capacity_label = tk.Label(self, text="Salvage at bag capacity (%):")
        salvage_capacity_label.grid(row=5, column=1, padx=10, pady=10, sticky=tk.E)
        salvage_capacity_scale = tk.Scale(self, variable=self.salv_capacity_var, from_=0, to=100, orient=tk.HORIZONTAL, length=100)
        salvage_capacity_scale.grid(row=5, column=2, padx=10, pady=0, sticky='we')

        # Create a label for the brightness
        bright_label = tk.Label(self, text="Select a brightness level (testing):")
        bright_label.grid(row=6, column=0, padx=10, pady=10, columnspan=3, sticky=tk.W)

        # Create a scale for the brightness
        self.bright_var = tk.IntVar()
        self.bright_var.set(50)
        bright_scale = tk.Scale(self, variable=self.bright_var, from_=0, to=100, orient=tk.HORIZONTAL, length=100)
        bright_scale.grid(row=7, column=0, padx=10, pady=0, columnspan=3, sticky='we')

        # Create a text box to display the log
        self.log_text = tk.Text(self, height=10, width=50)
        self.log_text.grid(row=8, column=0, padx=10, pady=0, columnspan=3, sticky='we')

        self.auto_fish_button = tk.Button(self, text="Auto Fishing", width=15, justify=tk.CENTER)
        self.trade_button = tk.Button(self, text="Trade Fish", width=15, justify=tk.CENTER)
        self.fish_button = tk.Button(self, text="Fish 1 Round", width=15, justify=tk.CENTER)
        self.salv_button = tk.Button(self, text="Auto Salvage", width=15, justify=tk.CENTER)
        self.auto_fish_button.grid(row=9, column=0, padx=10, pady=10, sticky=tk.W)
        self.trade_button.grid(row=9, column=1, padx=10, pady=10, sticky=tk.W)
        self.fish_button.grid(row=9, column=2, padx=10, pady=10, sticky=tk.W)
        self.salv_button.grid(row=10, column=0, padx=10, pady=10, sticky=tk.W)

