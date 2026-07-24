import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# opening DB connection, extracting data, loading it into DF and closing connection
db_path = "data/apple_silicon.db"
conn = sqlite3.connect(db_path)
sql = """
SELECT 
    chip_cpu_cores,
    chip_gpu_cores,
    chip_npu_tops,
    chip_mem_bw,
    chip_max_displays
FROM chip_configs;
"""
df = pd.read_sql_query(sql, conn)
conn.close()

# renaming columns and calculating correlations
rename_dict = {
    "chip_cpu_cores": "CPU Cores",
    "chip_gpu_cores": "GPU Cores",
    "chip_npu_tops": "NPU TOPS",
    "chip_mem_bw": "Memory Bandwidth",
    "chip_max_displays": "Max Displays",
}
df_curated = df.rename(columns=rename_dict)
corr = df_curated.corr()

# plot setup
sns.set_theme(style="white")
plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(8, 6.5))

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="Blues",
    vmax=1.0,
    vmin=0.0,
    square=True,
    linewidths=1.5,
    cbar_kws={"shrink": 0.8, "label": "Pearson Correlation (r)"},
    ax=ax,
)

# axis and title formatting
ax.set_title(
    "Hardware Correlation Matrix",
    fontsize=14,
    fontweight="bold",
    pad=20,
)
plt.xticks(rotation=45, ha="right", fontweight="bold")
plt.yticks(rotation=0, fontweight="bold")

plt.tight_layout()
plt.savefig("visualizations/1_correlation_matrix.png", dpi=300)
plt.close()