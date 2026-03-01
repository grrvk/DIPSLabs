# Lab 2 — Maximum Independent Set in a Tree

Finds a Maximum Independent Set (MIS) in a tree.

## Run

```bash
cd Lab2
uv sync
uv run main.py --nodes 10                # random tree, 10 nodes
uv run main.py --base star          # base star
```

## Options

- `--nodes` — number of nodes for random generation (default: 10)
- `--base` — use a base tree: `star`, `binary`