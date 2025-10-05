# Flows Prefect : Installation et utilisation - Projet M2 BI

> **Note**: Ce répertoire a été renommé de `prefect/` à `prefect_flows/` pour éviter les conflits avec le package Python `prefect`.

## Installation

```bash
uv sync
```

```bash
prefect-cloud login
```

## Usage

Pour tester votre flow localement avant de le déployer :

```bash
# Exécuter le pipeline complet
uv run python prefect_flows/pipeline.py
```

## Déploiement

```bash
# Deploy la pipeline
prefect-cloud deploy prefect_flows/pipeline.py:dbt_full_pipeline
```



```bash
# Liste deployments
prefect-cloud ls

# Run Instant
prefect-cloud run pipeline-dbt-complet

### Exécution récurrente

Pour run la pipeline automatiquement (ex: tous les jours à 9h) :

```bash
prefect-cloud schedule pipeline-dbt-complet --cron "0 9 * * *"
```

Expl de cron :
- `"0 9 * * *"` : Tous les jours à 9h
- `"0 */4 * * *"` : Toutes les 4 heures
- `"0 9 * * 1"` : Tous les lundis à 9h
- `"0 0 1 * *"` : Le 1er de chaque mois à minuit

## Docs

- [Prefect](https://docs.prefect.io/)
- [prefect-dbt](https://prefecthq.github.io/prefect-dbt/)
- [dbt](https://docs.getdbt.com/)

