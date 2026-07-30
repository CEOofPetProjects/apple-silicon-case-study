import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# opening DB connection, extracting data, loading it into DF and closing connection
db_path = "data/apple_silicon.db"
conn = sqlite3.connect(db_path)
sku_sql = """
SELECT 
    f.family_name,
    c.chip_name,
    cfg.config_id,
    cfg.chip_cpu_cores,
    cfg.chip_gpu_cores,
    COUNT(DISTINCT m.mem_option_id) AS num_memory_options,
    COUNT(DISTINCT s.storage_option_id) AS num_storage_options,
    (COUNT(DISTINCT m.mem_option_id) * COUNT(DISTINCT s.storage_option_id)) AS total_skus
FROM chip_configs cfg
JOIN chips c ON cfg.chip_id = c.chip_id
JOIN chip_families f ON c.family_id = f.family_id
LEFT JOIN chip_memory_options m ON cfg.config_id = m.config_id
LEFT JOIN chip_storage_options s ON cfg.config_id = s.config_id
GROUP BY cfg.config_id;
"""
df_sku = pd.read_sql_query(sku_sql, conn)
conn.close()

# aggregate total hardware specification profiles and unique configs per family generation
sku_summary = (
    df_sku.groupby("family_name")
    .agg(
        total_skus=("total_skus", "sum"),
        total_configs=("config_id", "count"),
        distinct_chips=("chip_name", "nunique"),
    )
    .reset_index()
)

print("\nSpecification profiles per generation")
print(sku_summary.to_string(index=False))

# plot setup
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "font.size": 10})
fig, ax1 = plt.subplots(figsize=(10, 6))

# primary axis: total hardware specification profiles
bars = ax1.bar(
    sku_summary["family_name"],
    sku_summary["total_skus"],
    color="#a1c9f4",
    edgecolor="#1f77b4",
    linewidth=1.2,
    alpha=0.85,
    width=0.45,
    label="Total specification profiles",
)

ax1.set_xlabel("Apple Silicon generation", fontweight="bold", labelpad=10)
ax1.set_ylabel("Total hardware specification profiles", fontweight="bold", color="#333333")
ax1.tick_params(axis="y", labelcolor="#333333")
ax1.set_ylim(0, max(sku_summary["total_skus"]) * 1.25)

# secondary axis: hardware binnings and chip models
ax2 = ax1.twinx()
ax2.grid(False)  # turning off secondary grid lines

line_configs = ax2.plot(
    sku_summary["family_name"],
    sku_summary["total_configs"],
    color="#d62728",
    marker="o",
    linewidth=2.5,
    markersize=7,
    label="Hardware binnings (configurations)",
    zorder=3,
)

line_chips = ax2.plot(
    sku_summary["family_name"],
    sku_summary["distinct_chips"],
    color="#2ca02c",
    marker="s",
    linewidth=2.5,
    markersize=7,
    linestyle="--",
    label="Distinct chip models",
    zorder=3,
)

ax2.set_ylabel(
    "Count (models, configurations)", fontweight="bold", color="#333333", labelpad=10
)
ax2.tick_params(axis="y", labelcolor="#333333")
max_secondary = max(
    max(sku_summary["total_configs"]), max(sku_summary["distinct_chips"])
)
ax2.set_ylim(0, max_secondary * 1.35)

# annotating inside the bottom of each bar
for p in bars:
    height = p.get_height()
    ax2.annotate(
        f"{int(height)} specs",
        (p.get_x() + p.get_width() / 2.0, 0),
        xycoords=ax1.transData,
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color="#0e487a",
        xytext=(0, 8),
        textcoords="offset points",
        zorder=10,
    )

# annotating data points on red and green lines
for x, y_cfg, y_chip in zip(
    sku_summary["family_name"],
    sku_summary["total_configs"],
    sku_summary["distinct_chips"]
):
    # hardware binnings labels
    ax2.annotate(
        f"{y_cfg} configs",
        (x, y_cfg),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=8.5,
        fontweight="bold",
        color="#d62728",
    )
    # chip models labels
    ax2.annotate(
        f"{y_chip} models",
        (x, y_chip),
        textcoords="offset points",
        xytext=(0, -14),
        ha="center",
        fontsize=8.5,
        fontweight="bold",
        color="#2ca02c",
    )

# combining 2 legends since there are 2 axis
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(
    lines_1 + lines_2,
    labels_1 + labels_2,
    loc="upper right",
    frameon=True,
    facecolor="white",
    framealpha=0.9,
)

plt.title(
    "Total hardware specification profiles in each Apple Silicon generation",
    fontsize=12,
    fontweight="bold",
    pad=15,
)
plt.tight_layout()
plt.savefig("visualizations/2_1_specs_all.png", dpi=300)
plt.close()