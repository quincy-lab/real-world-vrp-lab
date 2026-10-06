from pathlib import Path
from time import perf_counter
import csv

import numpy as np
import vrplib
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE = PROJECT_ROOT / "data" / "X-n101-k25.vrp"
RESULTS = PROJECT_ROOT / "results" / "ortools_x-n101-k25.csv"
ROUTES = PROJECT_ROOT / "results" / "ortools_x-n101-k25_routes.txt"

BEST_KNOWN = 27_591
NUM_VEHICLES = 25
TIME_LIMIT_SECONDS = 10


def main():
    # 1) Read the same CVRPLIB benchmark used by the PyVRP baseline.
    instance = vrplib.read_instance(INSTANCE)

    # Set X uses rounded Euclidean distances in benchmark evaluations.
    distance_matrix = np.floor(instance["edge_weight"] + 0.5).astype(np.int64)
    demands = instance["demand"].astype(np.int64)
    capacity = int(instance["capacity"])
    depot = int(instance["depot"][0])

    # 2) Manager: translates our node IDs to OR-Tools internal indices.
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        NUM_VEHICLES,
        depot,
    )

    # 3) Model: represents the routing decisions.
    routing = pywrapcp.RoutingModel(manager)

    # 4) Distance callback: tells OR-Tools the travel cost from A to B.
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node, to_node])

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    # 5) Demand callback + Capacity Dimension: enforce vehicle capacity 206.
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int(demands[from_node])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [capacity] * NUM_VEHICLES,
        True,
        "Capacity",
    )

    # 6) Search: build an initial solution, then improve it with GLS.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(TIME_LIMIT_SECONDS)

    start = perf_counter()
    solution = routing.SolveWithParameters(search_parameters)
    runtime = perf_counter() - start

    if solution is None:
        print("OR-Tools did not find a feasible solution.")
        return

    # 7) Extract routes and benchmark metrics.
    routes = []
    for vehicle_id in range(NUM_VEHICLES):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue

        index = routing.Start(vehicle_id)
        route = []

        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))

        route.append(manager.IndexToNode(index))
        routes.append(route)

    cost = int(solution.ObjectiveValue())
    gap_pct = 100 * (cost - BEST_KNOWN) / BEST_KNOWN

    print("\n=== OR-Tools experiment summary ===")
    print("instance      : X-n101-k25")
    print(f"customers     : {len(demands) - 1}")
    print(f"routes used   : {len(routes)}")
    print(f"solution cost : {cost}")
    print(f"best known    : {BEST_KNOWN}")
    print(f"gap (%)       : {gap_pct:.3f}")
    print(f"runtime (s)   : {runtime:.3f}")

    # 8) Save metrics for the later unified benchmark.
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    write_header = not RESULTS.exists()

    with RESULTS.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "instance",
                "method",
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
                "method": "OR-Tools",
                "time_limit_s": TIME_LIMIT_SECONDS,
                "customers": len(demands) - 1,
                "routes": len(routes),
                "cost": cost,
                "best_known": BEST_KNOWN,
                "gap_pct": round(gap_pct, 4),
                "runtime_s": round(runtime, 4),
            }
        )

    route_text = "\n".join(
        f"Route #{idx + 1}: " + " -> ".join(map(str, route))
        for idx, route in enumerate(routes)
    )
    ROUTES.write_text(route_text, encoding="utf-8")


if __name__ == "__main__":
    main()
