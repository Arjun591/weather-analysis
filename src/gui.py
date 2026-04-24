import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.charts import (plot_temperature_by_country, plot_temperature_trends,
                         plot_humidity, plot_precipitation,
                         plot_wind, plot_air_quality, plot_conditions,
                         plot_correlation_heatmap, plot_seasonal_analysis,
                         plot_year_over_year, plot_forecast,
                         plot_health_index, plot_climate_change)
from src.analysis import temperature_summary, forecast_for_date
from src.load_data import get_countries, get_cities, filter_by_country, filter_by_city, filter_by_date

class WeatherDashboard:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.filtered_df = df
        self.current_chart = "Temperature by Country"
        self.root.title("Weather Analysis Dashboard")
        self.root.geometry("1200x750")
        self.root.configure(bg="#1e1e2e")
        self.build_sidebar()
        self.build_main_area()
        self.show_chart("Temperature by Country")

    def build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg="#2e2e3e", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="Weather", font=("Arial", 16, "bold"),
                 bg="#2e2e3e", fg="white").pack(pady=10)

        # Country search
        tk.Label(self.sidebar, text="Search Country:",
                 bg="#2e2e3e", fg="#aaaaaa", font=("Arial", 9)).pack(pady=(5, 2))
        country_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        country_frame.pack(padx=10, pady=3, fill=tk.X)
        self.country_var = tk.StringVar()
        self.country_entry = tk.Entry(country_frame, textvariable=self.country_var,
                                       font=("Arial", 10), bg="#3e3e5e", fg="white",
                                       insertbackground="white", relief=tk.FLAT)
        self.country_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        self.country_entry.bind("<Return>", self.search_country)
        tk.Button(country_frame, text="", font=("Arial", 10),
                  bg="#5e5e9e", fg="white", relief=tk.FLAT,
                  cursor="hand2", command=self.search_country
                  ).pack(side=tk.RIGHT, ipady=4, ipadx=4)

        # City search
        tk.Label(self.sidebar, text="Search City:",
                 bg="#2e2e3e", fg="#aaaaaa", font=("Arial", 9)).pack(pady=(5, 2))
        city_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        city_frame.pack(padx=10, pady=3, fill=tk.X)
        self.city_var = tk.StringVar()
        self.city_entry = tk.Entry(city_frame, textvariable=self.city_var,
                                    font=("Arial", 10), bg="#3e3e5e", fg="white",
                                    insertbackground="white", relief=tk.FLAT)
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 5))
        self.city_entry.bind("<Return>", self.search_city)
        tk.Button(city_frame, text="", font=("Arial", 10),
                  bg="#5e5e9e", fg="white", relief=tk.FLAT,
                  cursor="hand2", command=self.search_city
                  ).pack(side=tk.RIGHT, ipady=4, ipadx=4)

        # Divider
        tk.Frame(self.sidebar, bg="#444455", height=1).pack(fill=tk.X, padx=10, pady=8)

        # Date range filter
        tk.Label(self.sidebar, text="DATE RANGE FILTER",
                 bg="#2e2e3e", fg="#aaaaaa", font=("Arial", 8)).pack(pady=(0, 3))

        years = sorted(self.df['last_updated'].dt.year.unique().tolist())
        months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
        year_strs = [str(y) for y in years]

        from_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        from_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(from_frame, text="From:", bg="#2e2e3e", fg="#aaaaaa",
                 font=("Arial", 9), width=5).pack(side=tk.LEFT)
        self.from_year = ttk.Combobox(from_frame, values=year_strs, width=6, state="readonly")
        self.from_year.set(year_strs[0])
        self.from_year.pack(side=tk.LEFT, padx=2)
        self.from_month = ttk.Combobox(from_frame, values=months, width=4, state="readonly")
        self.from_month.set("01")
        self.from_month.pack(side=tk.LEFT, padx=2)

        to_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        to_frame.pack(fill=tk.X, padx=10, pady=2)
        tk.Label(to_frame, text="To:", bg="#2e2e3e", fg="#aaaaaa",
                 font=("Arial", 9), width=5).pack(side=tk.LEFT)
        self.to_year = ttk.Combobox(to_frame, values=year_strs, width=6, state="readonly")
        self.to_year.set(year_strs[-1])
        self.to_year.pack(side=tk.LEFT, padx=2)
        self.to_month = ttk.Combobox(to_frame, values=months, width=4, state="readonly")
        self.to_month.set("12")
        self.to_month.pack(side=tk.LEFT, padx=2)

        btn_frame = tk.Frame(self.sidebar, bg="#2e2e3e")
        btn_frame.pack(fill=tk.X, padx=10, pady=4)
        tk.Button(btn_frame, text="Apply", font=("Arial", 9),
                  bg="#5e5e9e", fg="white", relief=tk.FLAT,
                  cursor="hand2", command=self.apply_date_filter
                  ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))
        tk.Button(btn_frame, text="Reset", font=("Arial", 9),
                  bg="#3e3e5e", fg="white", relief=tk.FLAT,
                  cursor="hand2", command=self.reset_date_filter
                  ).pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Divider
        tk.Frame(self.sidebar, bg="#444455", height=1).pack(fill=tk.X, padx=10, pady=8)

        tk.Label(self.sidebar, text="GLOBAL CHARTS", bg="#2e2e3e",
         fg="#aaaaaa", font=("Arial", 8)).pack(pady=(0, 3))
        chart_options = [
             "Temperature by Country",
            "Temperature Trends",
            "Humidity",
            "Precipitation",
            "Wind Speed",
            "Air Quality",
            "Weather Conditions",
            "Correlation Heatmap",
            "Seasonal Analysis",
            "Year over Year",
            "Health Index",
            "Climate Change",
            ]
        self.global_chart_var = tk.StringVar(value="Temperature by Country")
        chart_dropdown = ttk.Combobox(self.sidebar, textvariable=self.global_chart_var,
                               values=chart_options, state="readonly", width=24)
        chart_dropdown.pack(padx=10, pady=3, fill=tk.X)

        tk.Button(self.sidebar, text="Show Chart", font=("Arial", 9),
          bg="#5e5e9e", fg="white", relief=tk.FLAT, cursor="hand2",
          command=lambda: self.show_chart(self.global_chart_var.get())
          ).pack(fill=tk.X, padx=10, pady=3)
        tk.Frame(self.sidebar, bg="#444455", height=1).pack(fill=tk.X, padx=10, pady=8)
        self.stats_label = tk.Label(self.sidebar, text="", bg="#2e2e3e",
                                     fg="#cccccc", font=("Arial", 9), justify=tk.LEFT)
        self.stats_label.pack(padx=10)
        self.update_stats(self.filtered_df)

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
            "Temperature by Country": lambda: plot_temperature_by_country(self.filtered_df),
            "Temperature Trends":     lambda: plot_temperature_trends(self.filtered_df),
            "Humidity":               lambda: plot_humidity(self.filtered_df),
            "Precipitation":          lambda: plot_precipitation(self.filtered_df),
            "Wind Speed":             lambda: plot_wind(self.filtered_df),
            "Air Quality":            lambda: plot_air_quality(self.filtered_df),
            "Weather Conditions":     lambda: plot_conditions(self.filtered_df),
            "Correlation Heatmap":    lambda: plot_correlation_heatmap(self.filtered_df),
            "Seasonal Analysis":      lambda: plot_seasonal_analysis(self.filtered_df),
            "Year over Year":         lambda: plot_year_over_year(self.filtered_df),
            "Health Index":           lambda: plot_health_index(self.filtered_df),
            "Climate Change":         lambda: plot_climate_change(self.filtered_df),
        }
        figure = chart_map[chart_name]()
        canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(figure)

    def apply_date_filter(self):
        start = f"{self.from_year.get()}-{self.from_month.get()}-01"
        end = f"{self.to_year.get()}-{self.to_month.get()}-31"
        self.filtered_df = filter_by_date(self.df, start, end)
        if len(self.filtered_df) == 0:
            messagebox.showwarning("No Data", "No data found for selected date range.")
            self.filtered_df = self.df
            return
        self.update_stats(self.filtered_df)
        self.show_chart(self.current_chart)

    def reset_date_filter(self):
        self.filtered_df = self.df
        self.update_stats(self.filtered_df)
        self.show_chart(self.current_chart)

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
        avg_humidity = round(filtered_df['humidity'].mean(), 1)
        avg_wind = round(filtered_df['wind_kph'].mean(), 1)
        avg_pm25 = round(filtered_df['air_quality_PM2.5'].mean(), 1)

        # Header
        header = tk.Frame(self.chart_frame, bg="#1e1e2e")
        header.pack(fill=tk.X, pady=(0, 5))
        tk.Button(header, text="← Back", font=("Arial", 10),
                  bg="#3e3e5e", fg="white", relief=tk.FLAT,
                  cursor="hand2", padx=10, pady=5,
                  command=lambda: self.show_chart(self.current_chart)
                  ).pack(side=tk.LEFT, padx=10)
        tk.Label(header, text=f"{icon} {name}",
                 font=("Arial", 14, "bold"),
                 bg="#1e1e2e", fg="white").pack(side=tk.LEFT, padx=20)

        # Temperature cards
        tk.Label(self.chart_frame, text="Temperature",
                 font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#aaaaaa"
                 ).pack(anchor="w", padx=15)
        temp_frame = tk.Frame(self.chart_frame, bg="#1e1e2e")
        temp_frame.pack(fill=tk.X, padx=10, pady=2)
        for title, value, color in [
            ("Avg", f"{stats['mean']}°C", "#e74c3c"),
            ("Max", f"{stats['max']}°C", "#e67e22"),
            ("Min", f"{stats['min']}°C", "#3498db"),
            ("Std", f"{stats['std']}°C", "#9b59b6"),
            ("Records", f"{len(filtered_df):,}", "#2ecc71"),
        ]:
            card = tk.Frame(temp_frame, bg=color, padx=10, pady=6)
            card.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
            tk.Label(card, text=title, font=("Arial", 8), bg=color, fg="white").pack()
            tk.Label(card, text=value, font=("Arial", 10, "bold"), bg=color, fg="white").pack()

        tk.Label(self.chart_frame, text="Other Stats",
                 font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#aaaaaa"
                 ).pack(anchor="w", padx=15, pady=(5, 0))
        other_frame = tk.Frame(self.chart_frame, bg="#1e1e2e")
        other_frame.pack(fill=tk.X, padx=10, pady=2)
        for title, value, color in [
            ("Humidity", f"{avg_humidity}%", "#1abc9c"),
            ("Wind", f"{avg_wind} kph", "#3498db"),
            ("PM2.5", f"{avg_pm25}", "#e67e22"),
        ]:
            card = tk.Frame(other_frame, bg=color, padx=10, pady=6)
            card.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
            tk.Label(card, text=title, font=("Arial", 8), bg=color, fg="white").pack()
            tk.Label(card, text=value, font=("Arial", 10, "bold"), bg=color, fg="white").pack()

        # Chart selector + forecast button
        controls = tk.Frame(self.chart_frame, bg="#1e1e2e")
        controls.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(controls, text="Chart:", bg="#1e1e2e",
                 fg="#aaaaaa", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))

        chart_options = ["Temperature Trends", "Weather Conditions",
                         "Humidity", "Precipitation", "Wind Speed",
                         "Seasonal Analysis", "Year over Year", "Forecast (7 days)"]
        self.info_chart_var = tk.StringVar(value="Temperature Trends")
        chart_dropdown = ttk.Combobox(controls, textvariable=self.info_chart_var,
                                       values=chart_options, state="readonly", width=22)
        chart_dropdown.pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Show Chart", font=("Arial", 9),
                  bg="#5e5e9e", fg="white", relief=tk.FLAT, cursor="hand2",
                  command=lambda: self.show_info_chart(filtered_df)
                  ).pack(side=tk.LEFT, padx=5)

        # Forecast for specific date
        tk.Label(controls, text="Forecast date:",
                 bg="#1e1e2e", fg="#aaaaaa", font=("Arial", 9)
                 ).pack(side=tk.LEFT, padx=(20, 5))
        self.forecast_date_var = tk.StringVar(value="2026-06-01")
        tk.Entry(controls, textvariable=self.forecast_date_var,
                 font=("Arial", 10), bg="#3e3e5e", fg="white",
                 insertbackground="white", relief=tk.FLAT, width=12
                 ).pack(side=tk.LEFT, ipady=4)
        tk.Button(controls, text="Forecast", font=("Arial", 9),
                  bg="#e74c3c", fg="white", relief=tk.FLAT, cursor="hand2",
                  command=lambda: self.show_date_forecast(filtered_df, name)
                  ).pack(side=tk.LEFT, padx=5)

        # Chart area
        self.info_chart_frame = tk.Frame(self.chart_frame, bg="#1e1e2e")
        self.info_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Show default chart
        self.show_info_chart(filtered_df)

    def show_info_chart(self, filtered_df):
        for widget in self.info_chart_frame.winfo_children():
            widget.destroy()

        chart_name = self.info_chart_var.get()
        chart_map = {
            "Temperature Trends":   lambda: plot_temperature_trends(filtered_df),
            "Weather Conditions":   lambda: plot_conditions(filtered_df),
            "Humidity":             lambda: plot_humidity(filtered_df),
            "Precipitation":        lambda: plot_precipitation(filtered_df),
            "Wind Speed":           lambda: plot_wind(filtered_df),
            "Seasonal Analysis":    lambda: plot_seasonal_analysis(filtered_df),
            "Year over Year":       lambda: plot_year_over_year(filtered_df),
            "Forecast (7 days)":    lambda: plot_forecast(filtered_df, days=7),
        }
        figure = chart_map[chart_name]()
        canvas = FigureCanvasTkAgg(figure, master=self.info_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(figure)

    def show_date_forecast(self, filtered_df, name):
        target_date = self.forecast_date_var.get().strip()
        try:
            result = forecast_for_date(filtered_df, target_date)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid date format. Use YYYY-MM-DD\n{e}")
            return

        msg = (f"Forecast for {name} on {target_date}:\n\n"
               f"Temperature: {result.get('temperature_celsius', 'N/A')}°C\n"
               f"Humidity: {result.get('humidity', 'N/A')}%\n"
               f"Wind Speed: {result.get('wind_kph', 'N/A')} kph\n"
               f"Pressure: {result.get('pressure_mb', 'N/A')} mb\n\n"
               f"Note: This is a trend-based estimate.")
        messagebox.showinfo("Weather Forecast", msg)

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