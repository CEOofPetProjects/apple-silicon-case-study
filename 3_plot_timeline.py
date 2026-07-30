import sqlite3
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# using month labels for translations
month_labels = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

db_path = "data/apple_silicon.db"
conn = sqlite3.connect(db_path)
sql = """
SELECT 
    f.family_name,
    c.chip_name,
    c.chip_announcement_date
FROM chips c
JOIN chip_families f ON c.family_id = f.family_id;
"""
df = pd.read_sql_query(sql, conn)
conn.close()

df["chip_announcement_date"] = pd.to_datetime(df["chip_announcement_date"])

gen_timeline = (
    df.groupby("family_name")
    .agg(
        first_release=("chip_announcement_date", "min"),
        last_release=("chip_announcement_date", "max"),
        chip_count=("chip_name", "count"),
    )
    .reset_index()
)

gen_order = ["M1", "M2", "M3", "M4", "M5"]
gen_timeline["family_name"] = pd.Categorical(
    gen_timeline["family_name"], categories=gen_order, ordered=True
)
gen_timeline = gen_timeline.sort_values("family_name").reset_index(drop=True)

# plot setup
sns.set_theme(style="whitegrid")
plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(12, 6))
colors = ["#457B9D", "#2A9D8F", "#E76F51", "#1D3557", "#E63946"]

for idx, row in gen_timeline.iterrows():
    y_pos = idx
    color = colors[idx % len(colors)]
    gen_chips = df[df["family_name"] == row["family_name"]].sort_values(
        "chip_announcement_date"
    )

    # drawing horizontal line span
    ax.plot(
        [row["first_release"], row["last_release"]],
        [y_pos, y_pos],
        color=color,
        linewidth=4,
        solid_capstyle="round",
        zorder=2,
    )

    # drawing individual chip release points
    ax.scatter(
        gen_chips["chip_announcement_date"],
        [y_pos] * len(gen_chips),
        color=color,
        s=80,
        zorder=3,
        edgecolor="white",
        linewidth=1.5,
    )

    duration_days = (row["last_release"] - row["first_release"]).days
    duration_months = round(duration_days / 30.44, 1)
    start_str = f"{month_labels[row['first_release'].month]} {row['first_release'].year}"
    end_str = f"{month_labels[row['last_release'].month]} {row['last_release'].year}"

    ax.text(
        row["last_release"] + pd.Timedelta(days=25),
        y_pos,
        f"{start_str} – {end_str} ({duration_months} mo)",
        va="center",
        ha="left",
        fontsize=10,
        fontweight="bold",
        color="#2B2B2B",
    )

ax.set_yticks(range(len(gen_order)))
ax.set_yticklabels(gen_order, fontsize=12)

# splitting years into 4 parts
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))

# creating ruler-style physical tick marks on the x-axis
ax.tick_params(
    axis="x",
    which="major",
    length=8,
    width=1.5,
    color="#333333",
    direction="out",
)
ax.tick_params(
    axis="x",
    which="minor",
    length=4,
    width=1.0,
    color="#666666",
    direction="out",
)

min_date = pd.to_datetime("2020-06-01")
max_date = pd.to_datetime("2026-10-01")
ax.set_xlim(min_date, max_date)
ax.set_ylim(-0.5, len(gen_order) - 0.5)

ax.set_title(
    "Timeline of Apple Silicon generation rollouts",
    fontsize=14,
    fontweight="bold",
    pad=20,
)
ax.set_xlabel(
    "Announcement date",
    fontweight="bold",
    labelpad=10,
)
ax.set_ylabel("Apple Silicon generation", fontweight="bold")

# grid styling
ax.grid(True, which="major", linestyle="-", alpha=0.8, color="#B0B0B0")
ax.grid(True, which="minor", linestyle="--", alpha=0.5, color="#D0D0D0")

plt.tight_layout()
plt.savefig("visualizations/3_rollout_timeline.png", dpi=300)
plt.close()