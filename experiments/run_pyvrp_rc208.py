from pathlib import Path

from pyvrp import read, solve
from pyvrp.stop import MaxRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE = PROJECT_ROOT / "data" / "RC208.vrp"

# Best-known distance under the DIMACS one-decimal rounding convention.
BEST_KNOWN = 776.1
TIME_LIMIT_SECONDS = 10
SEED = 42


def benchmark_gap(cost, best_known=BEST_KNOWN):
    return 100 * (cost - best_known) / best_known


def main():
    # RC208 is a Solomon VRPTW instance converted to VRPLIB format.
    # DIMACS rounding keeps one decimal place internally by scaling by 10.
    data = read(INSTANCE, round_func="dimacs")

    result = solve(
        data,
        stop=MaxRuntime(TIME_LIMIT_SECONDS),
        seed=SEED,
        display=True,
    )

    # PyVRP's DIMACS convention stores 1 decimal as an integer scale of 10.
    cost = result.cost() / 10
    routes = result.best.routes()

    print("\n=== PyVRP VRPTW experiment summary ===")
    print(f"instance      : {INSTANCE.stem}")
    print(f"customers     : {data.num_clients}")
    print(f"routes used   : {len(routes)}")
    print(f"solution cost : {cost:.1f}")
    print(f"best known    : {BEST_KNOWN:.1f}")
    print(f"gap (%)       : {benchmark_gap(cost):.3f}")
    print(f"runtime (s)   : {result.runtime:.3f}")


if __name__ == "__main__":
    main()
