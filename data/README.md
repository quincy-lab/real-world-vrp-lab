# Benchmark data

## X-n101-k25

This project starts with the standard **X-n101-k25** Capacitated Vehicle Routing Problem (CVRP) benchmark instance.

- 1 depot + 100 customers
- vehicle capacity: 206
- best-known / proven optimal objective used in our first benchmark: **27591**
- distance convention: rounded Euclidean distance

Source used for the instance file:
- ML4VRP 2026 benchmark repository: `ML4VRP/ML4VRP2026`
- original X benchmark family: Uchoa et al., *New benchmark instances for the Capacitated Vehicle Routing Problem*

We use public benchmark data first so results can be compared against known references. Later stages will add real-road-network routing data.
