# Lab 4 — Dining philosophers

Solve the dining philosophers problem (each in a separate thread) for:
1.    N = 5 using a single counting semaphore;
2.    N = 5 using a mutex and five semaphores for forks.


## Run

```bash
cd Lab4
uv sync
uv run main.py --solution 1
```

## Options

- `--solution` — solution version: `1`, `2` or `1.1`