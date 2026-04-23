import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.charts import (plot_temperature_by_country, plot_temperature_trends,
                         plot_humidity, plot_precipitation,
                         plot_wind, plot_air_quality, plot_conditions)
from src.analysis import temperature_summary
from src.load_data import get_countries, get_cities, filter_by_country, filter_by_city

class WeatherDashboard:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.current_chart = "Temperature by Country"
        self.root.title("🌤️ Weather Analysis Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e2e")
        self.build_sidebar()
        self.build_main_area()
        self.show_chart("Temperature by Country")

    def build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#2e2e3e", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🌤️ Weather", font=("Arial", 16, "bold"),
                 bg="#2e2e3e", fg="white").pack(pady=20)

        # Country search
        tk.Label(self.sidebar, text="🌍 Search Country:",
                 bg="#2e2e3e", fg="#aaaaaa", font=("Arial", 9)).pack(pady=(10, 2))
        country_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        country_frame.pack(padx=10, pady=5, fill=tk.X)
        self.country_var = tk.StringVar()
        self.country_entry = tk.Entry(country_frame, textvariable=self.country_var,
                                       font=("Arial", 10), bg="#3e3e5e", fg="white",
                                       insertbackground="white", relief=tk.FLAT)
        self.country_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        self.country_entry.bind("<Return>", self.search_country)
        tk.Button(country_frame, text="🔍", font=("Arial", 10),
                  bg="#5e5e9e", fg="white", relief=tk.FLAT,
                  cursor="hand2", command=self.search_country
                  ).pack(side=tk.RIGHT, ipady=4, ipadx=4)

        # City search
        tk.Label(self.sidebar, text="🏙️ Search City:",
                 bg="#2e2e3e", fg="#aaaaaa", font=("Arial", 9)).pack(pady=(10, 2))
        city_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        city_frame.pack(padx=10, pady=5, fill=tk.X)
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(city_frame, textvariable=self.city_var,
                                    font=("Arial", 10), bg="#3e3e5e", fg="white",
                                    insertbackground="white", relief=tk.FLAT)
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        self.city_entry.bind("<Return>", self.search_city)
        tk.Button(city_frame, text="🔍", font=("Arial", 10),
                  bg="#5e5e9e", fg="white", relief=tk.FLAT,
                  cursor="hand2", command=self.search_city
                  ).pack(side=tk.RIGHT, ipady=4, ipadx=4)

        # Divider
        tk.Frame(self.sidebar, bg="#444455", height=1).pack(fill=tk.X, padx=10, pady=15)

        # Chart buttons
        tk.Label(self.sidebar, text="GLOBAL CHARTS", bg="#2e2e3e",
                 fg="#aaaaaa", font=("Arial", 8)).pack(pady=(0, 5))

        chart_buttons = [
            ("🌡️ Temperature by Country", "Temperature by Country"),
            ("📈 Temperature Trends",      "Temperature Trends"),
            ("💧 Humidity",                "Humidity"),
            ("🌧️ Precipitation",           "Precipitation"),
            ("💨 Wind Speed",              "Wind Speed"),
            ("😷 Air Quality",             "Air Quality"),
            ("⛅ Weather Conditions",      "Weather Conditions"),
        ]

        for label, chart_name in chart_buttons:
            btn = tk.Button(self.sidebar, text=label, font=("Arial", 9),
                            bg="#3e3e5e", fg="white", relief=tk.FLAT,
                            cursor="hand2", anchor="w", padx=10,
                            command=lambda c=chart_name: self.show_chart(c))
            btn.pack(fill=tk.X, padx=10, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#5e5e9e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3e3e5e"))

        tk.Frame(self.sidebar, bg="#444455", height=1).pack(fill=tk.X, padx=10, pady=15)
        self.stats_label = tk.Label(self.sidebar, text="", bg="#2e2e3e",
                                     fg="#cccccc", font=("Arial", 9), justify=tk.LEFT)
        self.stats_label.pack(padx=10)
        self.update_stats(self.df)

    def build_main_area(self):
        self.main_area = tk.Frame(self.root, bg="#1e1e2e")
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.chart_title = tk.Label(self.main_area, text="",
                                     font=("Arial", 14, "bold"),
                                     bg="#1e1e2e", fg="white")
        self.chart_title.pack(pady=10)
        self.chart_frame = tk.Frame(self.main_area, bg="#1e1e2e")
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

    def clear_main(self):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def show_chart(self, chart_name):
        self.clear_main()
        self.current_chart = chart_name
        self.chart_title.config(text=chart_name)
        chart_map = {
            "Temperature by Country": lambda: plot_temperature_by_country(self.df),
            "Temperature Trends":     lambda: plot_temperature_trends(self.df),
            "Humidity":               lambda: plot_humidity(self.df),
            "Precipitation":          lambda: plot_precipitation(self.df),
            "Wind Speed":             lambda: plot_wind(self.df),
            "Air Quality":            lambda: plot_air_quality(self.df),
            "Weather Conditions":     lambda: plot_conditions(self.df),
        }
        figure = chart_map[chart_name]()
        canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(figure)

    def search_country(self, event=None):
        query = self.country_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a country name.")
            return
        countries = get_countries(self.df)
        match = next((c for c in countries if c.lower() == query.lower()), None)
        if not match:
            matches = [c for c in countries if query.lower() in c.lower()]
            if len(matches) == 1:
                match = matches[0]
            elif len(matches) > 1:
                messagebox.showinfo("Multiple Matches",
                                    "Multiple countries found:\n" + "\n".join(matches) +
                                    "\n\nPlease be more specific.")
                return
            else:
                messagebox.showerror("Not Found", f"Country '{query}' not found.")
                return
        self.show_info_page(match, level="country")

    def search_city(self, event=None):
        query = self.city_var.get().strip()
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a city name.")
            return
        cities = get_cities(self.df)
        match = next((c for c in cities if c.lower() == query.lower()), None)
        if not match:
            matches = [c for c in cities if query.lower() in c.lower()]
            if len(matches) == 1:
                match = matches[0]
            elif len(matches) > 1:
                messagebox.showinfo("Multiple Matches",
                                    "Multiple cities found:\n" + "\n".join(matches) +
                                    "\n\nPlease be more specific.")
                return
            else:
                messagebox.showerror("Not Found", f"City '{query}' not found.")
                return
        self.show_info_page(match, level="city")

    def show_info_page(self, name, level="country"):
        self.clear_main()
        if level == "country":
            filtered_df = filter_by_country(self.df, name)
            icon = "🌍"
        else:
            filtered_df = filter_by_city(self.df, name)
            icon = "🏙️"
        stats = temperature_summary(filtered_df)

        # Header
        header = tk.Frame(self.chart_frame, bg="#1e1e2e")
        header.pack(fill=tk.X, pady=(0, 10))
        tk.Button(header, text="← Back", font=("Arial", 10),
                  bg="#3e3e5e", fg="white", relief=tk.FLAT,
                  cursor="hand2", padx=10, pady=5,
                  command=lambda: self.show_chart(self.current_chart)
                  ).pack(side=tk.LEFT, padx=10)
        tk.Label(header, text=f"{icon} {name}",
                 font=("Arial", 14, "bold"),
                 bg="#1e1e2e", fg="white").pack(side=tk.LEFT, padx=20)

        # Stats cards
        stats_frame = tk.Frame(self.chart_frame, bg="#1e1e2e")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        cards = [
            ("🌡️ Avg Temp",  f"{stats['mean']}°C",   "#e74c3c"),
            ("🔺 Max Temp",  f"{stats['max']}°C",    "#e67e22"),
            ("🔻 Min Temp",  f"{stats['min']}°C",    "#3498db"),
            ("📊 Std Dev",   f"{stats['std']}°C",    "#9b59b6"),
            ("📍 Records",   f"{len(filtered_df):,}", "#2ecc71"),
        ]
        for title, value, color in cards:
            card = tk.Frame(stats_frame, bg=color, padx=15, pady=10)
            card.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            tk.Label(card, text=title, font=("Arial", 9),
                     bg=color, fg="white").pack()
            tk.Label(card, text=value, font=("Arial", 13, "bold"),
                     bg=color, fg="white").pack()

        # Charts
        charts_frame = tk.Frame(self.chart_frame, bg="#1e1e2e")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.Frame(charts_frame, bg="#1e1e2e")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(left, text="Temperature Trends", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="white").pack()
        fig1 = plot_temperature_trends(filtered_df)
        c1 = FigureCanvasTkAgg(fig1, master=left)
        c1.draw()
        c1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig1)

        right = tk.Frame(charts_frame, bg="#1e1e2e")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(right, text="Weather Conditions", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="white").pack()
        fig2 = plot_conditions(filtered_df)
        c2 = FigureCanvasTkAgg(fig2, master=right)
        c2.draw()
        c2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig2)

    def update_stats(self, df):
        stats = temperature_summary(df)
        text = (f"Records: {len(df):,}\n"
                f"Avg Temp: {stats['mean']}°C\n"
                f"Max Temp: {stats['max']}°C\n"
                f"Min Temp: {stats['min']}°C")
        self.stats_label.config(text=text)


def run_dashboard(df):
    root = tk.Tk()
    app = WeatherDashboard(root, df)
    root.mainloop()