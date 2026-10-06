# Benchmark data

## X-n101-k25

This project starts with the standard **X-n101-k25** Capacitated Vehicle Routing Problem (CVRP) benchmark instance from **CVRPLIB Set X**.

- 1 depot + 100 customers
- vehicle capacity: 206
- optimal objective: **27,591**
- distance convention: rounded Euclidean distance
- CVRPLIB marks this instance as **optimal = yes**

### Canonical references

- CVRPLIB, Set X (Uchoa et al., 2017): https://galgos.inf.puc-rio.br/cvrplib/en/instances/1
- Uchoa, E., Pecin, D., Pessoa, A., Poggi, M., Vidal, T., & Subramanian, A. (2017). *New benchmark instances for the Capacitated Vehicle Routing Problem*. European Journal of Operational Research, 257(3), 845–858. https://doi.org/10.1016/j.ejor.2016.08.012

The X benchmark was introduced as a diverse CVRP benchmark for evaluating exact and heuristic algorithms, with 100 main instances ranging from 100 to 1,000 customers.

### File provenance

The current `X-n101-k25.vrp` file in this repository was initially obtained from the public `ML4VRP/ML4VRP2026` repository. We treat that repository only as a mirror/distribution source; the authoritative benchmark references for this project are **CVRPLIB and the original Uchoa et al. paper**.

We use standard public benchmark data first so results can be reproduced and compared against established references. Later stages will add real-road-network routing data.


## RC208 (Solomon VRPTW)

The second project stage introduces **VRPTW (Vehicle Routing Problem with Time Windows)** using the classical Solomon **RC208** instance.

- 1 depot + 100 customers
- vehicle capacity: 1,000
- service time: 10
- customer-specific hard time windows
- benchmark best-known distance used here: **776.1**
- distance/time convention: DIMACS one-decimal truncation

RC208 adds a scheduling dimension to CVRP: a vehicle may arrive before a customer's time window and wait, but service must start within the allowed interval. Capacity and routing constraints still apply.

### Canonical references

- Solomon, M. M. (1987). *Algorithms for the Vehicle Routing and Scheduling Problems with Time Window Constraints*. Operations Research, 35(2), 254-265.
- SINTEF Solomon VRPTW benchmark page: https://www.sintef.no/projectweb/top/vrptw/100-customers/
- PyVRP VRPTW benchmark documentation: https://pyvrp.org/setup/benchmarks.html

### File provenance

The local `RC208.vrp` and `RC208.sol` files are copied from the public `PyVRP/Instances` benchmark repository. PyVRP notes that the original Solomon instances are converted to VRPLIB format and that the tracked best-known solutions use the DIMACS one-decimal rounding convention. The benchmark itself originates from Solomon (1987); PyVRP/Instances is used as the reproducible distribution source.
