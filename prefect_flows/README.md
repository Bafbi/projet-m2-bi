# Pipeline dbt avec Prefect

Ce dossier contient les flows Prefect pour orchestrer l'exécution de dbt.

## 📋 Architecture

### Séparation des Responsabilités

L'architecture suit le principe de **séparation des responsabilités** (Separation of Concerns) :

1. **Configuration** (`infrastructure/setup_profiles/`) : 
   - Crée et configure les **Prefect Blocks** (credentials, profils, opérations)
   - S'exécute **une seule fois** lors du setup initial ou lors de changements de config
   - Stocke la configuration de manière centralisée dans Prefect Cloud

2. **Orchestration** (`prefect_flows/pipeline.py`) :
   - **Utilise** les blocs Prefect créés par le setup
   - S'exécute **à chaque run** de la pipeline
   - Charge dynamiquement la configuration selon l'environnement (dev/prod)

### Pourquoi cette Architecture ?

#### ✅ Avantages

1. **DRY (Don't Repeat Yourself)** : La configuration est définie une seule fois
2. **Sécurité** : Les credentials sont stockés de manière sécurisée dans Prefect
3. **Flexibilité** : Changement d'environnement via un simple paramètre
4. **Traçabilité** : Tous les runs utilisent la même configuration versionée
5. **Scalabilité** : Facile d'ajouter de nouveaux environnements (staging, test, etc.)

#### 🔄 Pattern "Configuration as Code"

```
┌─────────────────────────────────────────┐
│  1. Infrastructure Setup                │
│  (Run once or on config changes)        │
│                                          │
│  terraform apply                         │
│  └─> Creates GCP resources              │
│                                          │
│  python -m infrastructure.setup_profiles │
│  └─> Creates Prefect Blocks:            │
│      • gcp-credentials                   │
│      • dbt-cli-profile-dev               │
│      • dbt-cli-profile-prod              │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  2. Pipeline Execution                   │
│  (Run frequently)                        │
│                                          │
│  python prefect_flows/pipeline.py        │
│  └─> Loads: dbt-cli-profile-{target}    │
│  └─> Executes: dbt run, dbt test        │
└─────────────────────────────────────────┘
```

## 🚀 Utilisation

### Prérequis

Assurez-vous d'avoir exécuté le setup des blocs Prefect :

```bash
# Setup complet (profiles locaux + blocs Prefect)
uv run python -m infrastructure.setup_profiles

# Ou seulement les blocs Prefect
uv run python -m infrastructure.setup_profiles --blocks-only
```

### Exécution Locale

#### Environnement Dev (par défaut)

```bash
uv run python prefect_flows/pipeline.py
```

Ce qui se passe en coulisses :
1. La pipeline charge le bloc `dbt-cli-profile-dev`
2. Ce bloc contient :
   - Le projet GCP
   - Le dataset dev
   - Les credentials GCP
   - 1 thread d'exécution
3. dbt s'exécute sur l'environnement dev

#### Environnement Prod

Pour exécuter sur prod, modifiez l'appel dans `pipeline.py` :

```python
if __name__ == "__main__":
    dbt_full_pipeline(target="prod")
```

Puis exécutez :

```bash
uv run python prefect_flows/pipeline.py
```

### Exécution avec Prefect Cloud

#### 1. Créer un Deployment

```bash
# Créer le deployment pour dev
prefect deployment build prefect_flows/pipeline.py:dbt_full_pipeline \
  -n "dbt-dev" \
  -p default-pool \
  --param target=dev

# Appliquer le deployment
prefect deployment apply dbt_full_pipeline-deployment.yaml
```

#### 2. Exécuter le Deployment

```bash
# Via CLI
prefect deployment run pipeline-dbt-complet/dbt-dev

# Avec un paramètre différent
prefect deployment run pipeline-dbt-complet/dbt-dev --param target=prod
```

#### 3. Scheduler un Deployment

```bash
# Run quotidien à 2h du matin
prefect deployment schedule create pipeline-dbt-complet/dbt-dev \
  --cron "0 2 * * *"
```

## 🔍 Concepts Techniques

### 1. Prefect Blocks

Les **Blocks** sont des objets de configuration réutilisables dans Prefect. Ils permettent de :
- Stocker des credentials de manière sécurisée
- Partager la configuration entre plusieurs flows
- Versionner la configuration
- Éviter la duplication de code

#### Blocks Créés par le Setup

| Bloc | Type | Description |
|------|------|-------------|
| `gcp-credentials` | `GcpCredentials` | Credentials GCP (service account) |
| `dbt-cli-profile-dev` | `DbtCliProfile` | Profil dbt pour dev (1 thread, dataset dev) |
| `dbt-cli-profile-prod` | `DbtCliProfile` | Profil dbt pour prod (4 threads, dataset prod) |
| `bigquery-target-configs-dev` | `BigQueryTargetConfigs` | Config BigQuery pour dev |
| `bigquery-target-configs-prod` | `BigQueryTargetConfigs` | Config BigQuery pour prod |

### 2. Chargement Dynamique

Le code utilise le **pattern de chargement dynamique** :

```python
# Construction dynamique du nom du bloc
profile_block_name = f"dbt-cli-profile-{target}"  # "dbt-cli-profile-dev" ou "dbt-cli-profile-prod"

# Chargement du bloc depuis Prefect
dbt_cli_profile = DbtCliProfile.load(profile_block_name)
```

**Pourquoi ?** Cela permet de :
- Changer d'environnement sans modifier le code
- Ajouter de nouveaux environnements facilement (staging, test, etc.)
- Centraliser la gestion des environnements

### 3. Gestion des Erreurs

Le code implémente une **gestion d'erreur explicite** :

```python
try:
    dbt_cli_profile = DbtCliProfile.load(profile_block_name)
except ValueError as e:
    logger.error("❌ Impossible de charger le bloc")
    logger.error("Assurez-vous d'avoir exécuté le setup")
    raise ValueError("Instructions détaillées...") from e
```

**Pourquoi ?** Pour guider l'utilisateur en cas de problème et éviter des erreurs cryptiques.

### 4. Retry Strategy

Les tâches utilisent une **stratégie de retry** :

```python
@task(name="dbt-run", retries=2, retry_delay_seconds=30)
```

**Pourquoi ?** 
- BigQuery peut avoir des erreurs temporaires (rate limiting, timeouts)
- Les retries automatiques améliorent la robustesse
- 2 retries = 3 tentatives au total (initial + 2 retries)

## 🎯 Prochaines Étapes

### Développement de Modèles dbt

Maintenant que la pipeline est configurée, vous pouvez :

1. **Créer vos modèles** dans `dbt/models/`
2. **Tester localement** :
   ```bash
   cd dbt
   dbt run --target dev
   dbt test --target dev
   ```
3. **Exécuter via Prefect** :
   ```bash
   uv run python prefect_flows/pipeline.py
   ```

### Extension de la Pipeline

Vous pouvez ajouter d'autres tâches dbt :

```python
@task(name="dbt-docs-generate")
def generate_dbt_docs(target: str = "dev"):
    """Génère la documentation dbt"""
    # ...
    
@task(name="dbt-snapshot")
def run_dbt_snapshots(target: str = "dev"):
    """Exécute les snapshots dbt"""
    # ...
```

### Monitoring et Alertes

Configurez des alertes Prefect pour être notifié en cas d'échec :

```python
from prefect.blocks.notifications.slack import SlackWebhook

@flow(on_failure=[SlackWebhook.load("my-slack-webhook")])
def dbt_full_pipeline(target: str = "dev"):
    # ...
```

## 📚 Ressources

- [Documentation Prefect](https://docs.prefect.io/)
- [Documentation dbt](https://docs.getdbt.com/)
- [Prefect-dbt Integration](https://prefecthq.github.io/prefect-dbt/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
