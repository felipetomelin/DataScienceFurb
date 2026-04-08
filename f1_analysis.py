"""
F1 2026 — Australian Grand Prix FP1
Dataset: All Laps 15032026.csv
Analysis: LEC, HAM, VER, LIN
Charts: Lap time stats, speed telemetry, driving style
"""

import csv
import json
import statistics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from collections import defaultdict
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
csv.field_size_limit(10**7)

DATA_FILE = Path(__file__).parent / "All Laps 15032026.csv"
DRIVERS   = ["LEC", "HAM", "VER", "LIN"]
COLORS    = {"LEC": "#E8002D", "HAM": "#27F4D2", "VER": "#3671C6", "LIN": "#FF8000"}
MIN_LAP   = 78   # seconds — filter out-laps / cool-down laps below this
MAX_LAP   = 110  # seconds — filter very slow laps

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
print("Loading data...")
rows = []
with open(DATA_FILE, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

print(f"  Total laps: {len(rows)}")

# ─────────────────────────────────────────────
# METRIC HELPERS
# ─────────────────────────────────────────────
def get_clean_laps(driver):
    """Return valid lap durations for a driver (filtered)."""
    laps = []
    for r in rows:
        if r["driver"] != driver:
            continue
        try:
            t = float(r["lap_duration"])
            if MIN_LAP <= t <= MAX_LAP:
                laps.append(t)
        except ValueError:
            pass
    return laps


def get_fastest_lap_telemetry(driver):
    """Return telemetry list for the driver's fastest valid lap."""
    best_time = float("inf")
    best_tel  = None
    for r in rows:
        if r["driver"] != driver:
            continue
        try:
            t = float(r["lap_duration"])
        except ValueError:
            continue
        tel_raw = r.get("telemetry", "").strip()
        if MIN_LAP <= t < best_time and tel_raw.startswith("["):
            best_time = t
            best_tel  = json.loads(tel_raw)
    return best_time, best_tel


# ─────────────────────────────────────────────
# COMPUTE METRICS
# ─────────────────────────────────────────────
print("Computing metrics...")

lap_stats   = {}   # driver -> {best, mean, median, std, laps}
tel_stats   = {}   # driver -> {speed_peak, speed_mean, speed_median,
                   #            throttle_pct, brake_pct, coast_pct, lap_time, trace}

for drv in DRIVERS:
    laps = get_clean_laps(drv)
    lap_stats[drv] = {
        "best":   min(laps),
        "mean":   statistics.mean(laps),
        "median": statistics.median(laps),
        "std":    statistics.stdev(laps) if len(laps) > 1 else 0,
        "laps":   laps,
    }

    best_time, tel = get_fastest_lap_telemetry(drv)
    if tel:
        speeds    = [s["speed"]    for s in tel]
        throttles = [s["throttle"] for s in tel]
        brakes    = [s["brake"]    for s in tel]
        n = len(tel)
        tel_stats[drv] = {
            "lap_time":       best_time,
            "speed_peak":     max(speeds),
            "speed_mean":     statistics.mean(speeds),
            "speed_median":   statistics.median(speeds),
            "throttle_pct":   sum(1 for t in throttles if t == 100) / n * 100,
            "brake_pct":      sum(brakes) / n * 100,
            "coast_pct":      sum(1 for i in range(n) if throttles[i] < 100 and brakes[i] == 0) / n * 100,
            "speeds":         speeds,
            "times":          [s["t"] for s in tel],
        }

# Print summary table
print(f"\n{'Driver':<6} {'Best':>8} {'Mean':>8} {'Median':>8} {'Std':>6} {'Laps':>5}")
print("-" * 45)
for drv in DRIVERS:
    s = lap_stats[drv]
    print(f"{drv:<6} {s['best']:>8.3f} {s['mean']:>8.3f} {s['median']:>8.3f} {s['std']:>6.3f} {len(s['laps']):>5}")

print(f"\n{'Driver':<6} {'Best Lap':>9} {'Peak km/h':>10} {'Mean km/h':>10} {'Median':>8} {'Throttle%':>10} {'Brake%':>7}")
print("-" * 65)
for drv in DRIVERS:
    t = tel_stats[drv]
    print(f"{drv:<6} {t['lap_time']:>9.3f} {t['speed_peak']:>10} {t['speed_mean']:>10.1f} {t['speed_median']:>8.1f} {t['throttle_pct']:>10.1f} {t['brake_pct']:>7.1f}")

# ─────────────────────────────────────────────
# PLOT STYLE
# ─────────────────────────────────────────────
plt.style.use("dark_background")
sns.set_context("talk")

FIG_BG  = "#0F0F0F"
AX_BG   = "#1A1A1A"
GRID_C  = "#2E2E2E"
TEXT_C  = "#E0E0E0"

def style_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(AX_BG)
    ax.tick_params(colors=TEXT_C, labelsize=10)
    ax.spines["bottom"].set_color(GRID_C)
    ax.spines["left"].set_color(GRID_C)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=GRID_C, linestyle="--", linewidth=0.6)
    ax.set_axisbelow(True)
    if title:  ax.set_title(title,  color=TEXT_C, fontsize=13, fontweight="bold", pad=10)
    if xlabel: ax.set_xlabel(xlabel, color=TEXT_C, fontsize=10)
    if ylabel: ax.set_ylabel(ylabel, color=TEXT_C, fontsize=10)


# ══════════════════════════════════════════════
# FIGURE 1 — LAP TIME STATS
# Best, Mean, Median + Std Dev error bars
# ══════════════════════════════════════════════
print("\nGenerating Figure 1: Lap Time Stats...")

fig1, axes = plt.subplots(1, 2, figsize=(16, 6))
fig1.patch.set_facecolor(FIG_BG)
fig1.suptitle("F1 2026 — Australian GP FP1 | Lap Time Analysis (LEC · HAM · VER · LIN)",
              color=TEXT_C, fontsize=14, fontweight="bold", y=1.01)

# ── 1a: Grouped bars: best / mean / median ──
ax = axes[0]
style_ax(ax, "Best · Mean · Median Lap Time", ylabel="Lap Time (s)")
x     = np.arange(len(DRIVERS))
width = 0.22
metrics = [("Best", "best", 0.85), ("Mean", "mean", 1.0), ("Median", "median", 0.7)]
offsets = [-width, 0, width]

for (label, key, alpha), offset in zip(metrics, offsets):
    vals = [lap_stats[d][key] for d in DRIVERS]
    bars = ax.bar(x + offset, vals, width, label=label,
                  color=[COLORS[d] for d in DRIVERS], alpha=alpha,
                  edgecolor="none")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f"{v:.2f}", ha="center", va="bottom", color=TEXT_C, fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(DRIVERS)
ax.set_ylim(78, 110)
legend_patches = [mpatches.Patch(color="white", alpha=a, label=l) for l, _, a in metrics]
ax.legend(handles=legend_patches, facecolor="#222", edgecolor="none", labelcolor=TEXT_C, fontsize=9)

# ── 1b: Std Dev (consistency) ──
ax = axes[1]
style_ax(ax, "Consistency — Std Dev of Lap Times\n(lower = more consistent)", ylabel="Std Dev (s)")
stds  = [lap_stats[d]["std"] for d in DRIVERS]
bars  = ax.bar(DRIVERS, stds, color=[COLORS[d] for d in DRIVERS], edgecolor="none", width=0.5)
for bar, v in zip(bars, stds):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            f"{v:.2f}s", ha="center", va="bottom", color=TEXT_C, fontsize=10)
ax.set_ylim(0, max(stds) * 1.35)

fig1.tight_layout()
fig1.savefig(Path(__file__).parent / "chart1_laptime_stats.png", dpi=150,
             bbox_inches="tight", facecolor=FIG_BG)
plt.show()
print("  Saved: chart1_laptime_stats.png")


# ══════════════════════════════════════════════
# FIGURE 2 — BOX PLOT: LAP TIME DISTRIBUTION
# ══════════════════════════════════════════════
print("Generating Figure 2: Box Plot...")

fig2, ax = plt.subplots(figsize=(12, 6))
fig2.patch.set_facecolor(FIG_BG)
style_ax(ax, "Lap Time Distribution — Box Plot (clean laps only)", ylabel="Lap Time (s)")

data_list  = [lap_stats[d]["laps"] for d in DRIVERS]
bp = ax.boxplot(data_list, patch_artist=True, widths=0.45,
                medianprops=dict(color="white", linewidth=2),
                whiskerprops=dict(color=GRID_C),
                capprops=dict(color=GRID_C),
                flierprops=dict(marker="o", markersize=4, color="#888"))

for patch, drv in zip(bp["boxes"], DRIVERS):
    patch.set_facecolor(COLORS[drv])
    patch.set_alpha(0.75)

# Annotate median values
for i, drv in enumerate(DRIVERS, 1):
    med = lap_stats[drv]["median"]
    ax.text(i, med + 0.4, f"{med:.2f}s", ha="center", color="white", fontsize=9, fontweight="bold")

ax.set_xticks(range(1, len(DRIVERS)+1))
ax.set_xticklabels(DRIVERS)
ax.set_ylim(75, 115)

# Annotate peaks (max clean lap) and best
for i, drv in enumerate(DRIVERS, 1):
    laps = lap_stats[drv]["laps"]
    ax.text(i, max(laps) + 0.5, f"⬆ {max(laps):.1f}s", ha="center", color="#888", fontsize=8)
    ax.text(i, min(laps) - 1.5, f"⬇ {min(laps):.3f}s", ha="center", color=COLORS[drv], fontsize=8, fontweight="bold")

fig2.tight_layout()
fig2.savefig(Path(__file__).parent / "chart2_boxplot.png", dpi=150,
             bbox_inches="tight", facecolor=FIG_BG)
plt.show()
print("  Saved: chart2_boxplot.png")


# ══════════════════════════════════════════════
# FIGURE 3 — TELEMETRY SPEED STATS
# Peak / Mean / Median speed on fastest lap
# ══════════════════════════════════════════════
print("Generating Figure 3: Speed Stats...")

fig3, ax = plt.subplots(figsize=(13, 6))
fig3.patch.set_facecolor(FIG_BG)
style_ax(ax, "Speed Analysis on Fastest Lap — Peak · Mean · Median (km/h)", ylabel="Speed (km/h)")

x     = np.arange(len(DRIVERS))
width = 0.22
speed_metrics = [("Peak",   "speed_peak",   1.0),
                 ("Mean",   "speed_mean",   0.75),
                 ("Median", "speed_median", 0.5)]

for (label, key, alpha), offset in zip(speed_metrics, [-width, 0, width]):
    vals = [tel_stats[d][key] for d in DRIVERS]
    bars = ax.bar(x + offset, vals, width, label=label,
                  color=[COLORS[d] for d in DRIVERS], alpha=alpha, edgecolor="none")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{v:.0f}", ha="center", va="bottom", color=TEXT_C, fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels([f"{d}\n({tel_stats[d]['lap_time']:.3f}s)" for d in DRIVERS])
ax.set_ylim(0, 380)

legend_patches = [mpatches.Patch(color="white", alpha=a, label=l) for l, _, a in speed_metrics]
ax.legend(handles=legend_patches, facecolor="#222", edgecolor="none", labelcolor=TEXT_C, fontsize=9)

fig3.tight_layout()
fig3.savefig(Path(__file__).parent / "chart3_speed_stats.png", dpi=150,
             bbox_inches="tight", facecolor=FIG_BG)
plt.show()
print("  Saved: chart3_speed_stats.png")


# ══════════════════════════════════════════════
# FIGURE 4 — DRIVING STYLE
# % Full Throttle / % Braking / % Coasting
# ══════════════════════════════════════════════
print("Generating Figure 4: Driving Style...")

fig4, ax = plt.subplots(figsize=(12, 5))
fig4.patch.set_facecolor(FIG_BG)
style_ax(ax, "Driving Style on Fastest Lap — Throttle · Braking · Coasting (%)")

throttle_pcts = [tel_stats[d]["throttle_pct"] for d in DRIVERS]
brake_pcts    = [tel_stats[d]["brake_pct"]    for d in DRIVERS]
coast_pcts    = [tel_stats[d]["coast_pct"]    for d in DRIVERS]

y     = np.arange(len(DRIVERS))
height = 0.55

b1 = ax.barh(y, throttle_pcts, height, label="Full Throttle (100%)",
             color=[COLORS[d] for d in DRIVERS], alpha=0.9)
b2 = ax.barh(y, brake_pcts, height, left=throttle_pcts, label="Braking",
             color="white", alpha=0.35)
b3 = ax.barh(y, coast_pcts, height,
             left=[t + b for t, b in zip(throttle_pcts, brake_pcts)],
             label="Coasting / Partial Throttle", color="#444")

# Annotate each segment
for i, drv in enumerate(DRIVERS):
    t = throttle_pcts[i]
    b = brake_pcts[i]
    c = coast_pcts[i]
    ax.text(t / 2,       i, f"{t:.1f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    ax.text(t + b / 2,   i, f"{b:.1f}%", ha="center", va="center", color="#111",  fontsize=9)
    ax.text(t + b + c/2, i, f"{c:.1f}%", ha="center", va="center", color="#bbb",  fontsize=9)

ax.set_yticks(y)
ax.set_yticklabels(DRIVERS)
ax.set_xlim(0, 105)
ax.set_xlabel("% of Fastest Lap Duration", color=TEXT_C, fontsize=10)
ax.xaxis.grid(True, color=GRID_C, linestyle="--", linewidth=0.6)
ax.yaxis.grid(False)
ax.legend(facecolor="#222", edgecolor="none", labelcolor=TEXT_C, fontsize=9, loc="lower right")

fig4.tight_layout()
fig4.savefig(Path(__file__).parent / "chart4_driving_style.png", dpi=150,
             bbox_inches="tight", facecolor=FIG_BG)
plt.show()
print("  Saved: chart4_driving_style.png")


# ══════════════════════════════════════════════
# FIGURE 5 — SPEED TRACE COMPARISON
# All 4 drivers' fastest laps overlaid
# ══════════════════════════════════════════════
print("Generating Figure 5: Speed Trace...")

fig5, ax = plt.subplots(figsize=(16, 6))
fig5.patch.set_facecolor(FIG_BG)
style_ax(ax, "Speed Trace — Fastest Lap Comparison (LEC · HAM · VER · LIN)",
         xlabel="Time into lap (s)", ylabel="Speed (km/h)")

for drv in DRIVERS:
    t  = tel_stats[drv]["times"]
    sp = tel_stats[drv]["speeds"]
    ax.plot(t, sp, color=COLORS[drv], linewidth=1.8, label=f"{drv}  ({tel_stats[drv]['lap_time']:.3f}s)",
            alpha=0.9)
    # Annotate peak speed
    peak_idx = sp.index(max(sp))
    ax.annotate(f"{max(sp)} km/h",
                xy=(t[peak_idx], sp[peak_idx]),
                xytext=(t[peak_idx] + 1, sp[peak_idx] + 5),
                color=COLORS[drv], fontsize=8, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=COLORS[drv], lw=0.8))

# Shade flat zones (speed < 150 km/h = slow corners)
ax.axhline(150, color="#555", linestyle=":", linewidth=1, label="150 km/h threshold (slow corners)")
ax.fill_between(tel_stats["LEC"]["times"],
                0, 150,
                where=[s < 150 for s in tel_stats["LEC"]["speeds"]],
                alpha=0.06, color="white", label="Slow corner zones (LEC ref)")

ax.set_ylim(0, 360)
ax.legend(facecolor="#1a1a1a", edgecolor="none", labelcolor=TEXT_C, fontsize=9, loc="upper left")

fig5.tight_layout()
fig5.savefig(Path(__file__).parent / "chart5_speed_trace.png", dpi=150,
             bbox_inches="tight", facecolor=FIG_BG)
plt.show()
print("  Saved: chart5_speed_trace.png")


print("\n✅ All charts generated successfully!")
print("Files saved in the same folder as this script:")
for i, name in enumerate(["chart1_laptime_stats.png", "chart2_boxplot.png",
                           "chart3_speed_stats.png", "chart4_driving_style.png",
                           "chart5_speed_trace.png"], 1):
    print(f"  {i}. {name}")
