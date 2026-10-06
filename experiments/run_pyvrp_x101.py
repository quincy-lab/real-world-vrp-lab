from pathlib import Path
import csv

from pyvrp import read, solve
from pyvrp.stop import MaxRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE = PROJECT_ROOT / "data" / "X-n101-k25.vrp"
RESULTS = PROJECT_ROOT / "results" / "pyvrp_x-n101-k25.csv"
ROUTES = PROJECT_ROOT / "results" / "pyvrp_x-n101-k25_routes.txt"

BEST_KNOWN = 27_591
TIME_LIMIT_SECONDS = 10
SEED = 42


def benchmark_gap(cost, best_known=BEST_KNOWN):
    return 100 * (cost - best_known) / best_known


def solve_pyvrp(instance=INSTANCE, time_limit=TIME_LIMIT_SECONDS, seed=SEED, display=False):
    """Solve one CVRP instance with PyVRP and return unified benchmark metrics."""
    data = read(instance, round_func="round")

    result = solve(
        data,
        stop=MaxRuntime(time_limit),
        seed=seed,
        display=display,
    )

    cost = int(result.cost())
    routes = result.best.routes()

    return {
        "instance": Path(instance).stem,
        "method": "PyVRP",
        "time_limit_s": time_limit,
        "customers": data.num_clients,
        "routes": len(routes),
        "cost": cost,
        "best_known": BEST_KNOWN,
        "benchmark_gap_pct": benchmark_gap(cost),
        "runtime_s": float(result.runtime),
        "route_text": str(result.best),
    }


def main():
    result = solve_pyvrp(display=True)

    print("\n=== PyVRP experiment summary ===")
    for key in [
        "instance",
        "customers",
        "routes",
        "cost",
        "best_known",
        "benchmark_gap_pct",
        "runtime_s",
    ]:
        value = result[key]
        if isinstance(value, float):
            value = f"{value:.3f}"
        print(f"{key:18}: {value}")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    write_header = not RESULTS.exists()
    csv_fields = [
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

    with RESULTS.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        if write_header:
            writer.writeheader()
        writer.writerow({key: result[key] for key in csv_fields})

    ROUTES.write_text(result["route_text"], encoding="utf-8")


if __name__ == "__main__":
    main()
