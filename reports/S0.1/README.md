# S0.1 — repository foundation

The CPU-first package, shared contracts, configuration groups, split manifest,
CI workflow and leakage tests are implemented. `make check` passes with seven
CPU tests. MuJoCo and GPU extras remain optional so the same contracts can be
validated on a Mac before A100 runs.
