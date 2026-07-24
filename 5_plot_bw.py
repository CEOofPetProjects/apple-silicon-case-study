import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

db_path = "data/apple_silicon.db"
conn = sqlite3.connect(db_path)
bw_sql = """
SELECT 
    f.family_name,
    c.chip_name,
    cfg.chip_mem_bw
FROM chip_configs cfg
JOIN chips c ON cfg.chip_id = c.chip_id
JOIN chip_families f ON c.family_id = f.family_id;
"""
df_bw = pd.read_sql_query(bw_sql, conn)
conn.close()

# mapping chips to hardware tiers
def assign_tier(name):
  if "A18" in name:
    return "Mobile (A18 Pro)"
  elif "Ultra" in name:
    return "Ultra"
  elif "Max" in name:
    return "Max"
  elif "Pro" in name:
    return "Pro"
  else:
    return "Base"

df_bw["tier"] = df_bw["chip_name"].apply(assign_tier)

# getting maximum bandwidth per tier per generation
bw_trend = (
    df_bw.groupby(["family_name", "tier"])["chip_mem_bw"].max().reset_index()
)

# defining explicit generation ordering and numerical positions
gen_order = ["M1", "M2", "M3", "M4", "M5"]
gen_map = {gen: i for i, gen in enumerate(gen_order)}

# mapping family names to numeric x-positions
bw_trend["x_pos"] = bw_trend["family_name"].map(gen_map)

# plot setup
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(10, 6))

tier_order = ["Mobile (A18 Pro)", "Base", "Pro", "Max", "Ultra"]
colors = {
    "Mobile (A18 Pro)": "#E63946",
    "Base": "#457B9D",
    "Pro": "#2A9D8F",
    "Max": "#E76F51",
    "Ultra": "#1D3557",
}

for tier in tier_order:
  subset = bw_trend[bw_trend["tier"] == tier].sort_values("x_pos")
  if not subset.empty:
    ax.plot(
        subset["x_pos"],
        subset["chip_mem_bw"],
        marker="o",
        linewidth=2.5,
        markersize=8,
        label=tier,
        color=colors.get(tier, "black"),
    )
    # adding bandwidth numbers above each data point
    for _, row in subset.iterrows():
      ax.annotate(
          f"{row['chip_mem_bw']:.0f} GB/s",
          (row["x_pos"], row["chip_mem_bw"]),
          textcoords="offset points",
          xytext=(0, 8),
          ha="center",
          fontsize=8,
      )

# enforcing correct x-axis labels
ax.set_xticks(range(len(gen_order)))
ax.set_xticklabels(gen_order)

ax.set_title(
    "Memory Bandwidth Scaling",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
ax.set_xlabel("Apple Silicon Generation", fontweight="bold")
ax.set_ylabel("Memory Bandwidth (GB/s)", fontweight="bold")
ax.legend(title="Chip Tier", frameon=True)
ax.grid(True, linestyle="--", alpha=0.6)
ax.set_ylim(0, 950)

plt.tight_layout()
plt.savefig("visualizations/5_bandwidth.png", dpi=300)
plt.close()