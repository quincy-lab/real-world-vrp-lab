from pathlib import Path
import csv

from run_pyvrp_x101 import solve_pyvrp
from run_ortools_x101 import solve_ortools
from run_copt_x101 import solve_copt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE = PROJECT_ROOT / "data" / "X-n101-k25.vrp"
OUTPUT = PROJECT_ROOT / "results" / "benchmark_x-n101-k25.csv"

TIME_LIMIT_SECONDS = 10

COMMON_FIELDS = [
    "instance",
    "method",
    "time_limit_s",
    "customers",
    "routes",
    "cost",
    "best_known",
    "benchmark_gap_pct",
    "runtime_s",
]


def main():
    solvers = [
        ("PyVRP", solve_pyvrp),
        ("OR-Tools", solve_ortools),
        ("COPT-MIP", solve_copt),
    ]

    results = []

    for name, solver in solvers:
        print(f"\n===== Running {name} =====")
        result = solver(INSTANCE, TIME_LIMIT_SECONDS)
        results.append(result)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COMMON_FIELDS)
        writer.writeheader()

        for result in results:
            writer.writerow({
                key: result[key]
                for key in COMMON_FIELDS
            })

    print("\n=== Unified benchmark ===")
    print(
        f"{'Method':<12}"
        f"{'Time(s)':>10}"
        f"{'Routes':>10}"
        f"{'Cost':>10}"
        f"{'Gap(%)':>12}"
    )

    for result in results:
        print(
            f"{result['method']:<12}"
            f"{result['runtime_s']:>10.3f}"
            f"{result['routes']:>10}"
            f"{result['cost']:>10}"
            f"{result['benchmark_gap_pct']:>12.3f}"
        )

    print(f"\nSaved: {OUTPUT}")


if __name__ == "__main__":
    main()
