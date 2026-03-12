# Lab 3 — Luby's Algorithm

Finds a Maximum Independent Set (MIS) in a graph.

## Run

```bash
cd Lab3
uv sync
uv run main.py --graph random --nodes 10 --prob 0.4 # random tree, 10 nodes, edge prob 0.4
uv run main.py --graph tree7                        # base binary tree
```

## Options

- `--nodes` — number of nodes for random generation (default: 10)
- `--prob` — probability of edge between two nodes in random generation  (default: 0.4)
- `--graph` — graph type: `random`, `path5`, `cycle6`, `k4`, `tree7`, `petersen`