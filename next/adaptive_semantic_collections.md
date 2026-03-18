# 🔮 Projet Futur : AdaptiveSemanticSet & AdaptiveSemanticDict

## Contexte

Les `SemanticSet` et `SemanticDict` actuels fonctionnent en **monde fermé** :
- Les clusters sont pré-générés à l'init via `emulate_iterator`
- Ils sont **fixes** : ajouter/supprimer un élément ne modifie jamais les clusters
- Un élément hors du domaine pré-calculé → `ValueError` (outlier)

Cette approche est **stable, prédictible et efficace** en exécution, mais elle ne peut pas s'adapter à un domaine qui évolue.

## Proposition : AdaptiveSemanticSet

Une variante **monde ouvert** où le clustering est **différé et incrémental** :

```python
adaptive_set = AdaptiveSemanticSet(axis="Concepts émergents", tolerance=0.15)

# Chaque ajout enrichit le nuage de points
adaptive_set.add("IA Générative")
adaptive_set.add("LLM")
adaptive_set.add("Blockchain")

# Le re-clustering est déclenché au moment de l'usage (lazy)
print(adaptive_set)          # → re-cluster si dirty
len(adaptive_set)            # → re-cluster si dirty
"IA" in adaptive_set         # → re-cluster si dirty
```

### Différences avec SemanticSet

| Aspect | SemanticSet (closed-world) | AdaptiveSemanticSet (open-world) |
|--------|---------------------------|----------------------------------|
| Clusters définis à | `__init__` (fixe) | chaque usage (lazy re-cluster) |
| `add()` hors domaine | `ValueError` | accepté, déclenche re-cluster |
| Coût de `add()` | O(1) — juste assignation | O(1) — stockage + flag dirty |
| Coût de `__len__`, `__contains__` | O(1) | O(n²) au pire (re-cluster) |
| Prédictibilité | ✅ Haute | ⚠️ Les clusters changent |
| Cas d'usage | Domaines bien définis | Exploration, monde ouvert |

### Défis d'implémentation

1. **Tractabilité** : Le re-clustering à chaque lecture est coûteux (embeddings + DBSCAN). Stratégies possibles :
   - Seuil de "saleté" : re-cluster seulement si N nouveaux éléments ajoutés depuis le dernier cluster
   - Clustering incrémental (ex: BIRCH, mini-batch K-Means)
   - Cache des embeddings déjà calculés

2. **Stabilité des labels** : Si les clusters changent, les labels changent aussi. L'utilisateur pourrait être surpris que `len(set)` retourne un résultat différent après un `add()`.

3. **Historique** : Conserver la liste ordonnée de toutes les interactions pour pouvoir rejouer/auditer.

### Priorité

🟡 **Moyenne** — Utile pour des cas d'exploration et de prototypage rapide, mais les `SemanticSet` en monde fermé couvrent la majorité des cas d'usage.
