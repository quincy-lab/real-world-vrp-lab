# Real-World VRP Lab

A reproducible benchmark project for comparing classical optimization, routing solvers, metaheuristics, and learning-based methods on vehicle routing problems.

## Goal

Build a unified experimental pipeline for Vehicle Routing Problems (VRP), starting from mature classical solvers and standard benchmarks, then extending to real-world constraints and learning-based optimization.

## Methods

- **PyVRP / ILS** — high-performance VRP solving and benchmark baseline
- **OR-Tools** — engineering-oriented routing solver
- **COPT** — mathematical programming / MIP formulation
- **Custom heuristics** — 2-opt and other neighborhood operators
- **Learning-based methods** — RL4CO / Attention Model, with road-network NCO as a later extension

## Evaluation

We compare methods using solution cost, best-known gap, runtime, scalability, and route visualizations. For MIP experiments we also distinguish solver proof gap from external benchmark gap.

## Project structure

```text
real-world-vrp-lab/
├── data/           # CVRPLIB / Solomon benchmark instances
├── src/            # solver wrappers and custom algorithms
├── experiments/    # reproducible experiment scripts
├── results/        # tables and logs
├── figures/        # route and benchmark visualizations
├── requirements.txt
├── requirements-learning.txt
└── README.md
```

## Progress

- [x] Standard CVRP benchmark (X-n101-k25)
- [x] Custom 2-opt neighborhood operator
- [x] PyVRP baseline
- [x] OR-Tools baseline
- [x] COPT MIP formulation and route extraction
- [x] Unified runtime-quality benchmark
- [x] CVRPTW / Solomon RC208 baseline
- [ ] RL4CO Attention Model: state -> action -> reward -> learning
- [ ] Classical vs learning-based evaluation
- [ ] Real-road-network extension

## Learning-based experiment

`experiments/run_rl4co_am_cvrp.py` is intentionally a small learning experiment rather than a competitive benchmark. It exposes the four pieces that matter for understanding neural combinatorial optimization:

```text
CVRPEnv state
    ↓
AttentionModelPolicy
    ↓
customer actions / route
    ↓
negative route length reward
    ↓
REINFORCE policy update
```

Learning dependencies are kept in `requirements-learning.txt` so the existing classical-OR environment remains independent. The learning stack is best run in a dedicated Python 3.12 environment before larger experiments are attempted.
