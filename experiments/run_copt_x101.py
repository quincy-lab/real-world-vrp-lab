from pathlib import Path
import csv

import numpy as np
import vrplib
import coptpy as cp
from coptpy import COPT


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE = PROJECT_ROOT / "data" / "X-n101-k25.vrp"
RESULTS = PROJECT_ROOT / "results" / "copt_x-n101-k25.csv"
ROUTES = PROJECT_ROOT / "results" / "copt_x-n101-k25_routes.txt"

BEST_KNOWN = 27_591
TIME_LIMIT_SECONDS = 10


def benchmark_gap(cost, best_known=BEST_KNOWN):
    return 100 * (cost - best_known) / best_known


def solve_copt(instance_path=INSTANCE, time_limit=TIME_LIMIT_SECONDS):
    """Solve one CVRP instance with a basic arc-flow MIP in COPT."""
    instance = vrplib.read_instance(instance_path)

    distance_matrix = np.floor(instance["edge_weight"] + 0.5).astype(np.int64)
    demands = instance["demand"].astype(np.int64)
    capacity = int(instance["capacity"])

    n = len(demands)
    customers = range(1, n)
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]

    env = cp.Envr()
    model = env.createModel("CVRP")

    # Binary routing decisions: x[i, j] = 1 iff arc i -> j is selected.
    x = model.addVars(arcs, vtype=COPT.BINARY, nameprefix="x")

    # Cumulative load after serving customer i.
    u = model.addVars(
        customers,
        lb=0,
        ub=capacity,
        vtype=COPT.CONTINUOUS,
        nameprefix="u",
    )

    model.setObjective(
        cp.quicksum(distance_matrix[i, j] * x[i, j] for i, j in arcs),
        COPT.MINIMIZE,
    )

    # Every customer is entered exactly once.
    for j in customers:
        model.addConstr(
            cp.quicksum(x[i, j] for i in range(n) if i != j) == 1
        )

    # Every customer is left exactly once.
    for i in customers:
        model.addConstr(
            cp.quicksum(x[i, j] for j in range(n) if j != i) == 1
        )

    # The number of routes leaving the depot equals the number returning.
    model.addConstr(
        cp.quicksum(x[0, j] for j in customers)
        == cp.quicksum(x[i, 0] for i in customers)
    )

    # Capacity bounds and MTZ-style load propagation / subtour elimination.
    for i in customers:
        model.addConstr(u[i] >= int(demands[i]))

    for i in customers:
        for j in customers:
            if i != j:
                model.addConstr(
                    u[j]
                    >= u[i]
                    + int(demands[j])
                    - capacity * (1 - x[i, j])
                )

    model.setParam(COPT.Param.TimeLimit, float(time_limit))
    model.solve()

    if not model.getAttr(COPT.Attr.HasSol):
        raise RuntimeError("COPT did not find a feasible solution.")

    selected_arcs = [
        (i, j)
        for i, j in arcs
        if x[i, j].x > 0.5
    ]

    next_node = {
        i: j
        for i, j in selected_arcs
        if i != 0
    }
    starts = [
        j
        for i, j in selected_arcs
        if i == 0
    ]

    routes = []
    for start in starts:
        route = [0, start]
        current = start

        while current != 0:
            current = next_node[current]
            route.append(current)

        routes.append(route)

    cost = int(round(model.getAttr(COPT.Attr.ObjVal)))
    best_bound = float(model.getAttr(COPT.Attr.ObjBound))
    mip_gap_pct = 100 * float(model.getAttr(COPT.Attr.BestGap))
    runtime = float(model.getAttr(COPT.Attr.SolvingTime))

    route_text = "\n".join(
        f"Route #{idx + 1}: " + " -> ".join(map(str, route))
        for idx, route in enumerate(routes)
    )

    return {
        "instance": Path(instance_path).stem,
        "method": "COPT-MIP",
        "time_limit_s": time_limit,
        "customers": n - 1,
        "routes": len(routes),
        "cost": cost,
        "best_known": BEST_KNOWN,
        "benchmark_gap_pct": benchmark_gap(cost),
        "runtime_s": runtime,
        "mip_best_bound": best_bound,
        "mip_gap_pct": mip_gap_pct,
        "route_text": route_text,
    }


def main():
    result = solve_copt()

    print("\n=== COPT experiment summary ===")
    for key in [
        "instance",
        "customers",
        "routes",
        "cost",
        "best_known",
        "benchmark_gap_pct",
        "mip_best_bound",
        "mip_gap_pct",
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
        "mip_best_bound",
        "mip_gap_pct",
    ]

    with RESULTS.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        if write_header:
            writer.writeheader()
        writer.writerow({key: result[key] for key in csv_fields})

    ROUTES.write_text(result["route_text"], encoding="utf-8")


if __name__ == "__main__":
    main()
