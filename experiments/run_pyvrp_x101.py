from pathlib import Path
import csv

from pyvrp import read, solve
from pyvrp.stop import MaxRuntime


INSTANCE = Path("data/X-n101-k25.vrp")
RESULTS = Path("results/pyvrp_x-n101-k25.csv")
ROUTES = Path("results/pyvrp_x-n101-k25_routes.txt")

BEST_KNOWN = 27_591
TIME_LIMIT_SECONDS = 10
SEED = 42


def main():
    # 1) Read a standard CVRP benchmark instance.
    # The X benchmark uses integer-rounded Euclidean distances.
    data = read(INSTANCE, round_func="round")

    # 2) Ask PyVRP to search for a good feasible solution.
    result = solve(
        data,
        stop=MaxRuntime(TIME_LIMIT_SECONDS),
        seed=SEED,
        display=True,
    )

    # 3) Extract the main experiment metrics.
    cost = result.cost()
    gap_pct = 100 * (cost - BEST_KNOWN) / BEST_KNOWN
    num_routes = len(result.best.routes())

    print("\n=== Experiment summary ===")
    print(f"instance      : X-n101-k25")
    print(f"customers     : {data.num_clients}")
    print(f"routes used   : {num_routes}")
    print(f"solution cost : {cost}")
    print(f"best known    : {BEST_KNOWN}")
    print(f"gap (%)       : {gap_pct:.3f}")
    print(f"runtime (s)   : {result.runtime:.3f}")

    # 4) Save one row that we can later compare with OR-Tools, COPT, etc.
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    write_header = not RESULTS.exists()

    with RESULTS.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "instance",
                "method",
                "seed",
                "time_limit_s",
                "customers",
                "routes",
                "cost",
                "best_known",
                "gap_pct",
                "runtime_s",
            ],
        )

        if write_header:
            writer.writeheader()

        writer.writerow(
            {
                "instance": "X-n101-k25",
                "method": "PyVRP",
                "seed": SEED,
                "time_limit_s": TIME_LIMIT_SECONDS,
                "customers": data.num_clients,
                "routes": num_routes,
                "cost": cost,
                "best_known": BEST_KNOWN,
                "gap_pct": round(gap_pct, 4),
                "runtime_s": round(result.runtime, 4),
            }
        )

    # 5) Save the actual routes for inspection.
    ROUTES.write_text(str(result.best), encoding="utf-8")


if __name__ == "__main__":
    main()
