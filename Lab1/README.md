# Lab 1 — Ring Leader Election

Implements a ring leader election algorithm. Nodes form a ring via pipes and elect the process with the highest UID (PID) as leader.

## Run

```bash
cd Lab1
uv sync          
uv run main.py   
uv run main.py -n 5   
```

Or with venv:

```bash
source .venv/bin/activate
python main.py -n 5
```

## Options

- `-n`, `--nodes` — number of nodes in the ring (default: 1, minimum: 2)
