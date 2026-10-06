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
NUM_VEHICLES = 100
TIME_LIMIT_SECONDS = 10


def benchmark_gap(cost, best_known=BEST_KNOWN):
    return 100 * (cost - best_known) / best_known


def solve_ortools(
    instance_path=INSTANCE,
    time_limit=TIME_LIMIT_SECONDS,
    num_vehicles=NUM_VEHICLES,
):
    """Solve one CVRP instance with OR-Tools and return unified benchmark metrics."""
    instance = vrplib.read_instance(instance_path)

    distance_matrix = np.floor(instance["edge_weight"] + 0.5).astype(np.int64)
    demands = instance["demand"].astype(np.int64)
    capacity = int(instance["capacity"])
    depot = int(instance["depot"][0])

    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix),
        num_vehicles,
        depot,
    )
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node, to_node])

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return int(demands[from_node])

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [capacity] * num_vehicles,
        True,
        "Capacity",
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(int(time_limit))

    start = perf_counter()
    solution = routing.SolveWithParameters(search_parameters)
    runtime = perf_counter() - start

    if solution is None:
        raise RuntimeError("OR-Tools did not find a feasible solution.")

    routes = []
    for vehicle_id in range(num_vehicles):
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
    route_text = "\n".join(
        f"Route #{idx + 1}: " + " -> ".join(map(str, route))
        for idx, route in enumerate(routes)
    )

    return {
        "instance": Path(instance_path).stem,
        "method": "OR-Tools",
        "time_limit_s": time_limit,
        "customers": len(demands) - 1,
        "routes": len(routes),
        "cost": cost,
        "best_known": BEST_KNOWN,
        "benchmark_gap_pct": benchmark_gap(cost),
        "runtime_s": runtime,
        "route_text": route_text,
    }


def main():
    result = solve_ortools()

    print("\n=== OR-Tools experiment summary ===")
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
