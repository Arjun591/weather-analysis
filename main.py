from src.database import fetch_data, insert_data, get_summary_stats
from src.load_data import load_data
from src.gui import run_dashboard

# Check if Atlas is empty
stats = get_summary_stats()
print(f"Records in Atlas: {stats['total_records']}")

if stats['total_records'] == 0:
    print("Atlas is empty! Reloading from CSV...")
    df = load_data()
    insert_data(df)
else:
    print("Loading from Atlas...")
    df = fetch_data()

run_dashboard(df)