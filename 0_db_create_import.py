import os
import sqlite3
import pandas as pd

excel_path = "data/apple_hardware.xlsx"
db_path = "data/apple_silicon.db"

# removing old database file if re-running
if os.path.exists(db_path):
    os.remove(db_path)

schema_sql = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS chip_families (
    family_id INTEGER PRIMARY KEY,
    family_name TEXT NOT NULL,
    family_node TEXT
);

CREATE TABLE IF NOT EXISTS chips (
    chip_id INTEGER PRIMARY KEY,
    chip_name TEXT NOT NULL,
    family_id INTEGER NOT NULL,
    chip_announcement_date TEXT,
    FOREIGN KEY (family_id) 
        REFERENCES chip_families (family_id) 
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chip_configs (
    config_id INTEGER PRIMARY KEY,
    chip_id INTEGER NOT NULL,
    chip_cpu_cores INTEGER,
    chip_eff_cores INTEGER,
    chip_perf_cores INTEGER,
    chip_super_cores INTEGER,
    chip_gpu_cores INTEGER,
    chip_npu_cores INTEGER,
    chip_npu_tops REAL,
    chip_mem_type TEXT,
    chip_mem_speed INTEGER,
    chip_mem_bw REAL,
    chip_max_displays INTEGER,
    FOREIGN KEY (chip_id) 
        REFERENCES chips (chip_id) 
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chip_memory_options (
    mem_option_id INTEGER PRIMARY KEY,
    config_id INTEGER NOT NULL,
    memory_size_gb INTEGER NOT NULL,
    FOREIGN KEY (config_id) 
        REFERENCES chip_configs (config_id) 
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chip_storage_options (
    storage_option_id INTEGER PRIMARY KEY,
    config_id INTEGER NOT NULL,
    storage_size_gb INTEGER NOT NULL,
    FOREIGN KEY (config_id) 
        REFERENCES chip_configs (config_id) 
        ON DELETE CASCADE
);
"""
conn = sqlite3.connect(db_path) # opening connection to DB (creating DB if it doesn't exist)
cursor = conn.cursor() # cursor executes SQL commands
cursor.executescript(schema_sql) # executing CREATE TABLE commands from above
conn.commit() # saving new tables to DB

# establishing table order to preserve integrity when loading data
table_order = [
    "chip_families",
    "chips",
    "chip_configs",
    "chip_memory_options",
    "chip_storage_options",
]

for table_name in table_order:
    print(f"Reading tab '{table_name}' from Excel...")
    df = pd.read_excel(excel_path, sheet_name=table_name)
    df.columns = df.columns.str.strip() # stripping hidden whitespace from excel headers

    if table_name == "chips":
        # cleaning and standardizing announcement dates into DB YYYY-MM-DD strings
        if "chip_announcement_date" in df.columns:
            df["chip_announcement_date"] = pd.to_datetime(
                df["chip_announcement_date"], errors="coerce"
            )
            df["chip_announcement_date"] = df[
                "chip_announcement_date"
            ].dt.strftime("%Y-%m-%d")
            df["chip_announcement_date"] = df["chip_announcement_date"].where(
                df["chip_announcement_date"].notnull(), None
            )

    # inserting rows into DB
    df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
    print(f"Successfully loaded '{table_name}' ({len(df)} rows)")

conn.close()
print("\nDatabase build complete! All tables are populated and linked")