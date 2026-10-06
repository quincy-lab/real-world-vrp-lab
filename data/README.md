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
