# Real-World VRP Lab

A reproducible benchmark project for comparing classical optimization, routing solvers, metaheuristics, and learning-based methods on vehicle routing problems.

## Goal

Build a unified experimental pipeline for Vehicle Routing Problems (VRP), starting from mature classical solvers and standard benchmarks, then extending to real-world road-network data and learning-based optimization.

## Planned methods

- **PyVRP / HGS** — high-performance VRP solving and benchmark baseline
- **OR-Tools** — engineering-oriented routing solver
- **COPT** — mathematical programming / MIP formulation
- **Custom heuristics** — nearest neighbor, 2-opt, simulated annealing
- **Learning-based methods** — RRNCO / RL4CO / Attention Model (later stage)

## Evaluation

We will compare methods using:

- solution cost
- optimality / best-known gap
- runtime
- scalability
- route visualization

## Project structure

```text
real-world-vrp-lab/
├── data/           # benchmark and real-world instances
├── src/            # solver wrappers and algorithms
├── experiments/    # reproducible experiment scripts
├── results/        # tables and logs
├── figures/        # route and benchmark visualizations
└── README.md
```

## Current stage

**Stage 1 — PyVRP + standard VRP benchmarks**

The first milestone is to run a mature VRP solver on standard benchmark instances, understand the input/output pipeline, and build a reproducible baseline before adding other solvers.
