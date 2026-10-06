from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "results" / "benchmark_x-n101-k25.csv"
GAP_OUTPUT = PROJECT_ROOT / "figures" / "benchmark_gap_vs_runtime.png"
ZOOM_OUTPUT = PROJECT_ROOT / "figures" / "heuristic_gap_vs_runtime.png"
COPT_OUTPUT = PROJECT_ROOT / "figures" / "copt_mip_gap_vs_runtime.png"


def plot_benchmark_gap(df):
    """Full-scale comparison across all three methods."""
    plt.figure()

    for method, group in df.groupby("method"):
        group = group.sort_values("runtime_s")
        plt.plot(
            group["runtime_s"],
            group["benchmark_gap_pct"],
            marker="o",
            label=method,
        )

    plt.xlabel("Runtime (s)")
    plt.ylabel("Benchmark gap (%)")
    plt.title("X-n101-k25: solution quality vs runtime")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(GAP_OUTPUT, dpi=180)
    plt.show()


def plot_heuristic_gap(df):
    """Zoomed view so the PyVRP / OR-Tools quality difference is readable."""
    zoom = df[df["method"].isin(["PyVRP", "OR-Tools"])].copy()

    plt.figure()
    for method, group in zoom.groupby("method"):
        group = group.sort_values("runtime_s")
        plt.plot(
            group["runtime_s"],
            group["benchmark_gap_pct"],
            marker="o",
            label=method,
        )

    plt.xlabel("Runtime (s)")
    plt.ylabel("Benchmark gap (%)")
    plt.title("X-n101-k25: heuristic solution quality vs runtime")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(ZOOM_OUTPUT, dpi=180)
    plt.show()


def plot_copt_mip_gap(df):
    """COPT's internal optimality-proof progress."""
    copt = df[df["method"] == "COPT-MIP"].copy()
    copt["mip_gap_pct"] = pd.to_numeric(copt["mip_gap_pct"], errors="coerce")
    copt = copt.dropna(subset=["mip_gap_pct"]).sort_values("runtime_s")

    if copt.empty:
        return

    plt.figure()
    plt.plot(
        copt["runtime_s"],
        copt["mip_gap_pct"],
        marker="o",
    )
    plt.xlabel("Runtime (s)")
    plt.ylabel("COPT MIP gap (%)")
    plt.title("X-n101-k25: COPT proof gap vs runtime")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(COPT_OUTPUT, dpi=180)
    plt.show()


def main():
    df = pd.read_csv(INPUT)
    GAP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    plot_benchmark_gap(df)
    plot_heuristic_gap(df)
    plot_copt_mip_gap(df)

    print(f"Saved: {GAP_OUTPUT}")
    print(f"Saved: {ZOOM_OUTPUT}")
    print(f"Saved: {COPT_OUTPUT}")


if __name__ == "__main__":
    main()
