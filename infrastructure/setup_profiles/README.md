# DBT Profile Setup

Module pour configurer les profils dbt localement et dans Prefect.

## Structure

```
infrastructure/setup_profiles/
├── __init__.py       # Point d'entrée du package
├── __main__.py       # CLI entry point
├── config.py         # Configuration et logging
├── tasks.py          # Tâches Prefect individuelles
└── flows.py          # Flows Prefect orchestrant les tâches
```

## Fonctionnalités

### 1. Génération de profils locaux
Parse un template `profiles.tpl.yml` avec les outputs Terraform pour générer `profiles.yml`.

### 2. Configuration de blocs Prefect
Crée automatiquement les blocs Prefect pour tous les targets définis dans le template :
- GCP Credentials
- BigQuery Target Configs (un par target)
- DBT CLI Profile (un par target)
- DBT Core Operation (un par target)

### 3. Configuration complète
Combine les deux modes ci-dessus.

## Usage

### Command-Line Interface

The module provides a CLI with multiple execution modes:

```bash
# Complete setup (local profiles + Prefect blocks)
uv run python -m infrastructure.setup_profiles

# Local profiles only
uv run python -m infrastructure.setup_profiles --local-only

# Prefect blocks only
uv run python -m infrastructure.setup_profiles --blocks-only

# With custom GCP project
uv run python -m infrastructure.setup_profiles --gcp-project mon-projet-gcp
```

### Python API

You can also use the module programmatically:

```python
from infrastructure.setup_profiles import (
    generate_local_profiles_pipeline,
    setup_dbt_blocks_pipeline,
    setup_dbt_complete_pipeline,
)

# Generate local profiles only
generate_local_profiles_pipeline()

# Setup Prefect blocks only
setup_dbt_blocks_pipeline(gcp_project="mon-projet")

# Complete setup (both local + blocks)
setup_dbt_complete_pipeline(gcp_project="mon-projet")
```

### Execution Modes

**1. Complete Setup** (default)
- Generates local `dbt/profiles.yml`
- Creates all Prefect blocks for each target
- Recommended for initial setup

**2. Local-Only Mode** (`--local-only`)
- Only generates `dbt/profiles.yml`
- Useful for local development without Prefect
- Fast execution

**3. Blocks-Only Mode** (`--blocks-only`)
- Only creates Prefect blocks
- Assumes local profiles already exist
- Useful for updating Prefect configuration

## Architecture

### Tasks (tasks.py)
Tâches atomiques Prefect pour chaque opération :
- `parse_template_targets` : Parse le template YAML pour extraire les targets
- `load_terraform_outputs` : Charge les outputs Terraform
- `build_profile_context` : Construit le contexte pour le template
- `render_profile_template` : Rend le template avec les variables
- `write_local_profile` : Écrit le profil local
- `setup_gcp_credentials` : Crée le bloc GCP credentials
- `setup_bigquery_target` : Crée le bloc BigQuery config
- `setup_dbt_profile` : Crée le bloc dbt profile
- `setup_dbt_operation` : Crée le bloc dbt operation

### Flows (flows.py)
Orchestration des tâches en pipelines :
- `generate_local_profiles_pipeline` : Pipeline de génération locale
- `setup_dbt_blocks_pipeline` : Pipeline de configuration Prefect
- `setup_dbt_complete_pipeline` : Pipeline complète

## Dépendances

Le module détecte automatiquement tous les targets définis dans `profiles.tpl.yml` et :
1. Parse la structure YAML pour identifier les targets (dev, prod, etc.)
2. Extrait les paramètres (threads, location) de chaque target
3. Récupère les datasets correspondants depuis les outputs Terraform
4. Crée un ensemble complet de blocs Prefect pour chaque target

## Exemple de template

```yaml
projet_m2_bi:
  target: dev
  outputs:
    dev:
      type: bigquery
      dataset: ${dev_dataset}
      threads: 1
      location: ${region}
    
    prod:
      type: bigquery
      dataset: ${prod_dataset}
      threads: 4
      location: ${region}
```

Cette structure générera :
- `dbt-cli-profile-dev` et `dbt-cli-profile-prod`
- `dbt-core-operation-dev` et `dbt-core-operation-prod`
- etc.
