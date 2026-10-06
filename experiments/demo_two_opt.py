from pathlib import Path

from pyvrp import read

from src.two_opt import route_distance, two_opt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCE = PROJECT_ROOT / "data" / "X-n101-k25.vrp"


def main():
    data = read(INSTANCE, round_func="round")
    distance_matrix = data.distance_matrix(0)

    # One deliberately poor but capacity-feasible route.
    # Location 0 is the depot. The customer demands on this route sum to 136,
    # which is below the vehicle capacity of 206.
    bad_route = [0, 29, 1, 15, 2, 11, 7, 0]

    before = route_distance(bad_route, distance_matrix)
    improved_route = two_opt(bad_route, distance_matrix)
    after = route_distance(improved_route, distance_matrix)

    print("=== 2-opt validation ===")
    print(f"before route    : {bad_route}")
    print(f"before distance : {before}")
    print(f"after route     : {improved_route}")
    print(f"after distance  : {after}")
    print(f"improvement     : {before - after}")


if __name__ == "__main__":
    main()
