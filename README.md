# PFGO-PathFinding-GraphOptimization
Developping an algorithm to find the best oriented graph disposition

## Implémentation actuelle

Le dépôt contient désormais un optimiseur de placement de noeuds sur grille pour graphes orientés :

- placement des noeuds sur des cases uniques ;
- minimisation de la somme des longueurs de chemins ;
- interdiction de croisement de chemins sauf sur une origine/destination commune ;
- interdiction de traverser un noeud qui n'est pas la destination du chemin.

### Utilisation rapide

```python
from graph_optimizer import GraphOptimizer

optimizer = GraphOptimizer(width=4, height=4)
result = optimizer.optimize(
    nodes=["A", "B", "C", "D"],
    edges=[("A", "C"), ("B", "D")],
)

print(result.positions)
print(result.paths)
print(result.total_length)
```

### Tests

```bash
python -m unittest -v
```
