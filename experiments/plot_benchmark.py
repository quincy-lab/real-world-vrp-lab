from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT = PROJECT_ROOT / "results" / "benchmark_x-n101-k25.csv"
OUTPUT = PROJECT_ROOT / "figures" / "benchmark_gap_vs_runtime.png"


def main():
    df = pd.read_csv(INPUT)

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

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=180)
    plt.show()

    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
