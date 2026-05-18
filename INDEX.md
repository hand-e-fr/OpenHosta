---
type: prototype
status: actif
ring: .org
branch: dev_version_5
parent_product: products/OpenHosta
created: 2026-05-17
---

# OpenHosta v5 — Prototype d'exploration

**Branche** : `dev_version_5`
**Remote** : `/home/ebatt/VSCode_GitRepos/OpenHosta.git`

## Mission

Exploration de la version 5 d'OpenHosta. Nouveau design, nouvelles fonctionnalités, POCs.

## Cycle de vie

| Transition | Critère |
|---|---|
| `→ products/` | Stable, validé par .org, merge vers `main` |
| `→ archive/` | Abandonné ou inactif > 30j |

## Gardes-fous

- Les changements ici ne touchent PAS `products/OpenHosta/` (clone separate)
- Export vers `main` uniquement après validation .org
- Pas de données clients dans ce prototype

## Liens

- Stable : [products/OpenHosta/](../../../../products/OpenHosta/) (branche `main`)
- Lab parent : [hand-e-lab-2026/INDEX.md](../../INDEX.md)
