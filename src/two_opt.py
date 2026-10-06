def route_distance(route, distance_matrix):
    """Returns the total distance of a depot-to-depot route."""
    return sum(
        distance_matrix[route[i], route[i + 1]]
        for i in range(len(route) - 1)
    )


def two_opt(route, distance_matrix):
    """Improves one route with simple 2-opt local search."""
    route = route.copy()

    improved = True
    while improved:
        improved = False

        # Pick two non-adjacent edges: (a, b) and (c, d).
        for i in range(len(route) - 3):
            for j in range(i + 2, len(route) - 1):
                a, b = route[i], route[i + 1]
                c, d = route[j], route[j + 1]

                old_distance = (
                    distance_matrix[a, b] + distance_matrix[c, d]
                )
                new_distance = (
                    distance_matrix[a, c] + distance_matrix[b, d]
                )

                # If reconnecting is shorter, reverse the middle segment.
                if new_distance < old_distance:
                    route[i + 1:j + 1] = route[i + 1:j + 1][::-1]
                    improved = True
                    break

            # Restart from the beginning after every accepted move.
            if improved:
                break

    return route
