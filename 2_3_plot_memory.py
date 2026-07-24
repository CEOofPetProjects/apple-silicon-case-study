import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns

# opening DB connection, extracting data, loading it into DF and closing connection
db_path = "data/apple_silicon.db"
conn = sqlite3.connect(db_path)
mem_sql = """
SELECT 
    f.family_name,
    CASE 
        WHEN c.chip_name LIKE 'A%' THEN 'A-Series'
        WHEN c.chip_name LIKE '%Ultra%' THEN 'Ultra'
        WHEN c.chip_name LIKE '%Max%' THEN 'Max'
        WHEN c.chip_name LIKE '%Pro%' THEN 'Pro'
        ELSE 'Base'
    END AS chip_tier,
    COUNT(DISTINCT m.memory_size_gb) AS total_mem_options
FROM chip_memory_options m
JOIN chip_configs cfg ON m.config_id = cfg.config_id
JOIN chips c ON cfg.chip_id = c.chip_id
JOIN chip_families f ON c.family_id = f.family_id
GROUP BY f.family_name, chip_tier;
"""
df_mem = pd.read_sql_query(mem_sql, conn)
conn.close()

# pivoting data for stacked bar plotting
mem_pivot = df_mem.pivot(
    index="family_name", columns="chip_tier", values="total_mem_options"
).fillna(0)

# defining tier order and consistent color palette
tier_order = ["A-Series", "Base", "Pro", "Max", "Ultra"]
colors = {
    "A-Series": "#8c564b",
    "Base": "#4c72b0",
    "Pro": "#55a868",
    "Max": "#c44e52",
    "Ultra": "#8172b0",
}
mem_pivot = mem_pivot.reindex(
    columns=[t for t in tier_order if t in mem_pivot.columns]
)

# plot setup
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "font.size": 10})
fig, ax = plt.subplots(figsize=(8, 6))

mem_pivot.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    color=[colors[col] for col in mem_pivot.columns],
    edgecolor="white",
    linewidth=1.2,
    width=0.5,
)

ax.set_title(
    "Distinct Memory Capacities by Chip Tier",
    fontsize=12,
    fontweight="bold",
    pad=15,
)
ax.set_xlabel("Apple Silicon Generation", fontweight="bold", labelpad=10)
ax.set_ylabel("Distinct Memory Capacities Count", fontweight="bold", labelpad=10)
ax.tick_params(axis="x", rotation=0)
ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))# forcing y-axis to strictly display whole integers
ax.legend(title="Chip Tier", frameon=True, facecolor="white", framealpha=0.9)

plt.tight_layout()
plt.savefig("visualizations/2_3_memory.png", dpi=300)
plt.close()
