import matplotlib.pyplot as plt

# =====================
# 1. Load data
# =====================
# On Kaggle, replace the path below with the actual input path, e.g.:
# DATA_PATH = "/kaggle/input/electricity-mix/electricity-prod-source-stacked.csv"
DATA_PATH = "/kaggle/input/hgfgfdgdsa/electricity-prod-source-stacked.csv"

df = pd.read_csv(DATA_PATH)

# Keep only columns we need
energy_cols = [
    c for c in df.columns
    if c.startswith("Other renewables")
    or c.startswith("Electricity from")
]
base_cols = ["Entity", "Code", "Year"]
df = df[base_cols + energy_cols]

# Helper: shorten column names (drop the long "adapted..." suffix)
rename_map = {c: c.split(" (adapted")[0] for c in energy_cols}
df = df.rename(columns=rename_map)
energy_cols_short = list(rename_map.values())

# =====================
# 2. Derived variables: world, fossil vs low-carbon
# =====================
world = df[df["Entity"] == "World"].copy()
world = world.sort_values("Year")

fossil_cols = [
    "Electricity from coal - TWh",
    "Electricity from gas - TWh",
    "Electricity from oil - TWh",
]

lowcarbon_cols = [
    "Electricity from nuclear - TWh",
    "Electricity from hydro - TWh",
    "Electricity from wind - TWh",
    "Electricity from solar - TWh",
    "Electricity from bioenergy - TWh",
    "Other renewables excluding bioenergy - TWh",
]

world["Total_TWh"] = world[energy_cols_short].sum(axis=1)
world["Fossil_TWh"] = world[fossil_cols].sum(axis=1)
world["LowCarbon_TWh"] = world[lowcarbon_cols].sum(axis=1)

world["Fossil_share"] = world["Fossil_TWh"] / world["Total_TWh"] * 100
world["LowCarbon_share"] = world["LowCarbon_TWh"] / world["Total_TWh"] * 100

# =====================
# 3. Subset for focus countries
# =====================
focus_countries = ["China", "United States", "India", "European Union (27)"]

df_focus = df[df["Entity"].isin(focus_countries)].copy()
df_focus = df_focus.sort_values(["Entity", "Year"])
df_focus["Total_TWh"] = df_focus[energy_cols_short].sum(axis=1)
df_focus["LowCarbon_TWh"] = df_focus[lowcarbon_cols].sum(axis=1)
df_focus["LowCarbon_share"] = df_focus["LowCarbon_TWh"] / df_focus["Total_TWh"] * 100

# =====================
# 4. Figure 1 – World mix (stacked area)
# =====================
plt.figure(figsize=(9, 5))

sources_order = [
    "Electricity from coal - TWh",
    "Electricity from gas - TWh",
    "Electricity from oil - TWh",
    "Electricity from nuclear - TWh",
    "Electricity from hydro - TWh",
    "Electricity from wind - TWh",
    "Electricity from solar - TWh",
    "Electricity from bioenergy - TWh",
    "Other renewables excluding bioenergy - TWh",
]

plt.stackplot(
    world["Year"],
    [world[c] for c in sources_order],
    labels=[
        s.replace("Electricity from ", "").replace(" - TWh", "")
        for s in sources_order
    ],
)

plt.plot(world["Year"], world["Total_TWh"],
         linewidth=2.5, label="Total generation (TWh)")

plt.xlabel("Year")
plt.ylabel("Electricity generation (TWh)")
plt.title("Global Electricity Generation Mix by Source (1985–2023)")
plt.legend(loc="upper left", ncol=2, fontsize=8)
plt.tight_layout()
plt.savefig("fig1_world_mix_area.png", dpi=300)
plt.show()

# =====================
# 5. Figure 2 – Fossil vs low-carbon share
# =====================
plt.figure(figsize=(7, 4))

plt.plot(world["Year"], world["Fossil_share"],
         label="Fossil fuels", linewidth=2)
plt.plot(world["Year"], world["LowCarbon_share"],
         label="Low-carbon sources", linewidth=2)

plt.axhline(50, linestyle="--", linewidth=1, alpha=0.7)
plt.xlabel("Year")
plt.ylabel("Share of total generation (%)")
plt.title("Fossil vs Low-carbon Share of Global Electricity")
plt.legend()
plt.tight_layout()
plt.savefig("fig2_world_share_lines.png", dpi=300)
plt.show()

# =====================
# 6. Figure 3 – Small multiples for key economies
# =====================
import seaborn as sns

g = sns.relplot(
    data=df_focus,
    x="Year",
    y="LowCarbon_share",
    col="Entity",
    kind="line",
    col_wrap=2,
    facet_kws={"sharex": True, "sharey": True},
)

g.set_axis_labels("Year", "Low-carbon share (%)")
g.set_titles("{col_name}")
g.fig.suptitle("Low-carbon Electricity Share for Key Economies", y=1.02)

plt.tight_layout()
g.savefig("fig3_lowcarbon_share_small_multiples.png", dpi=300)
plt.show()

# =====================
# 7. Figure 4 – Top 15 countries by low-carbon share (latest year)
# =====================
df_2023 = df[df["Year"] == df["Year"].max()].copy()
df_2023["Total_TWh"] = df_2023[energy_cols_short].sum(axis=1)
df_2023["LowCarbon_TWh"] = df_2023[lowcarbon_cols].sum(axis=1)
df_2023["LowCarbon_share"] = (
    df_2023["LowCarbon_TWh"] / df_2023["Total_TWh"] * 100
)

# Filter out very small systems to reduce noise
df_2023 = df_2023[df_2023["Total_TWh"] > 5]

top15 = df_2023.sort_values("LowCarbon_share", ascending=False).head(15)

plt.figure(figsize=(7, 5))
plt.barh(top15["Entity"], top15["LowCarbon_share"])
plt.xlabel("Low-carbon share of electricity (%)")
plt.title("Top 15 Electricity Systems by Low-carbon Share ({})".format(
    int(df_2023["Year"].max())
))
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("fig4_top15_lowcarbon.png", dpi=300)
plt.show()

# =====================
# 8. Integrated dashboard figure (main figure for the report)
# =====================
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(10, 8))
gs = GridSpec(2, 2, height_ratios=[2, 1.2])

# Panel A – world stacked area
ax1 = fig.add_subplot(gs[0, :])
ax1.stackplot(
    world["Year"],
    [world[c] for c in sources_order],
    labels=[
        s.replace("Electricity from ", "").replace(" - TWh", "")
        for s in sources_order
    ],
)
ax1.plot(world["Year"], world["Total_TWh"],
         linewidth=2.0, label="Total generation (TWh)")
ax1.set_ylabel("Generation (TWh)")
ax1.set_title("A. Global Electricity Generation Mix")
ax1.legend(loc="upper left", ncol=3, fontsize=7)

# Panel B – fossil vs low-carbon share
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(world["Year"], world["Fossil_share"],
         label="Fossil fuels", linewidth=2)
ax2.plot(world["Year"], world["LowCarbon_share"],
         label="Low-carbon", linewidth=2)
ax2.set_xlabel("Year")
ax2.set_ylabel("Share (%)")
ax2.set_title("B. Fossil vs Low-carbon Share")
ax2.legend(fontsize=7)

# Panel C – 2023 top-15 bar chart
ax3 = fig.add_subplot(gs[1, 1])
ax3.barh(top15["Entity"], top15["LowCarbon_share"])
ax3.set_xlabel("Low-carbon share (%)")
ax3.set_title("C. Leaders in Low-carbon Electricity ({})".format(
    int(df_2023["Year"].max())
))
ax3.invert_yaxis()

fig.suptitle("Energy Mix Transition – Global Overview and Leaders",
             fontsize=13, y=0.97)
plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("main_figure_energy_mix_dashboard.png", dpi=300)
plt.show()
