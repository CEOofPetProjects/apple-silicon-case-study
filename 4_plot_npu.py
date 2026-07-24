import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

db_path = "data/apple_silicon.db"
conn = sqlite3.connect(db_path)
sql = """
SELECT 
    f.family_name,
    c.chip_name,
    cfg.chip_npu_tops,
    cfg.chip_npu_cores
FROM chip_configs cfg
JOIN chips c ON cfg.chip_id = c.chip_id
JOIN chip_families f ON c.family_id = f.family_id;
"""
df = pd.read_sql_query(sql, conn)
conn.close()

# classifying chips by NPU die architecture
def assign_npu_group(name):
  if "Ultra" in name:
    return "Ultra (Dual NPU / 32 Cores)"
  else:
    return "Base / Pro / Max / A18 Pro (Single NPU / 16 Cores)"


df["npu_group"] = df["chip_name"].apply(assign_npu_group)

# aggregating max TOPS per generation and NPU architecture group
npu_trend = (
    df.groupby(["family_name", "npu_group"])["chip_npu_tops"]
    .max()
    .reset_index()
)

# enforcing strict chronological x-axis ordering
gen_order = ["M1", "M2", "M3", "M4", "M5"]
gen_map = {gen: i for i, gen in enumerate(gen_order)}
npu_trend["x_pos"] = npu_trend["family_name"].map(gen_map)

# plot setup
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(10, 6))

groups = [
    "Base / Pro / Max / A18 Pro (Single NPU / 16 Cores)",
    "Ultra (Dual NPU / 32 Cores)",
]
colors = {
    "Base / Pro / Max / A18 Pro (Single NPU / 16 Cores)": "#2A9D8F",
    "Ultra (Dual NPU / 32 Cores)": "#1D3557",
}
markers = {
    "Base / Pro / Max / A18 Pro (Single NPU / 16 Cores)": "o",
    "Ultra (Dual NPU / 32 Cores)": "s",
}

for group in groups:
  subset = npu_trend[npu_trend["npu_group"] == group].sort_values("x_pos")
  if not subset.empty:
    ax.plot(
        subset["x_pos"],
        subset["chip_npu_tops"],
        marker=markers[group],
        linewidth=3,
        markersize=9,
        label=group,
        color=colors[group],
    )
    # annotating TOPS values directly above data points
    for _, row in subset.iterrows():
      ax.annotate(
          f"{row['chip_npu_tops']:.1f} TOPS",
          (row["x_pos"], row["chip_npu_tops"]),
          textcoords="offset points",
          xytext=(0, 10),
          ha="center",
          fontsize=9,
          fontweight="bold",
      )

# formatting X-axis
ax.set_xticks(range(len(gen_order)))
ax.set_xticklabels(gen_order, fontsize=12)

# labels and styling
ax.set_title(
    "Neural Engine (NPU) Performance Scaling",
    fontsize=14,
    fontweight="bold",
    pad=20,
)
ax.set_xlabel("Apple Silicon Generation", fontweight="bold", labelpad=10)
ax.set_ylabel(
    "Performance in TOPS (Trillion Operations Per Second)", fontweight="bold"
)
ax.legend(title="NPU Architecture Tier", frameon=True, loc="upper left")
ax.set_ylim(0, 75)
ax.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
plt.savefig("visualizations/4_npu_tops.png", dpi=300)
plt.close()