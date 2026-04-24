import warnings
warnings.filterwarnings("ignore")

import os
import pickle
from src.gui import run_dashboard

CACHE_FILE = "cache.pkl"

def get_data():
    # Try Atlas first
    try:
        from src.database import fetch_data, get_summary_stats
        print("Trying to connect to MongoDB Atlas...")
        stats = get_summary_stats()
        print(f"Atlas connected! Records: {stats['total_records']}")
        df = fetch_data()
        return df
    except Exception as e:
        print(f"Atlas unavailable: {e}")
        print("Falling back to local cache...")

    # Fallback to cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            df = pickle.load(f)
        print(f"Loaded {len(df)} records from cache")
        return df

    # Nothing works
    print("No data source available!")
    return None

df = get_data()
if df is not None:
    run_dashboard(df)
else:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("No Data",
                         "Could not connect to Atlas and no cache found.\nPlease check your internet connection.")
    root.destroy()