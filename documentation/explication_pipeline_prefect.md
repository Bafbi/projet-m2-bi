# Explication de l'Architecture Pipeline Prefect + dbt

## 🎯 Problème Initial

Votre `pipeline.py` essayait de charger un profil dbt hardcodé avec :

```python
dbt_cli_profile = DbtCliProfile.load("profile").get_profile()
```

**Problème** : Ce bloc "profile" n'existait pas, car vos flows de setup créent des blocs avec des noms spécifiques (`dbt-cli-profile-dev`, `dbt-cli-profile-prod`).

## ✅ Solution Implémentée

### 1. Architecture à Deux Niveaux

J'ai modifié votre code pour suivre une **architecture en deux phases** :

```
Phase 1 : SETUP (une fois)              Phase 2 : EXECUTION (à chaque run)
─────────────────────────              ────────────────────────────────
infrastructure/setup_profiles/   →     prefect_flows/pipeline.py
Crée les blocs Prefect                 Utilise les blocs créés
```

### 2. Modifications Apportées

#### A) Ajout du Paramètre `target`

**Avant** :
```python
def run_dbt_models():
    dbt_cli_profile = DbtCliProfile.load("profile")  # Bloc hardcodé ❌
```

**Après** :
```python
def run_dbt_models(target: str = "dev"):
    profile_block_name = f"dbt-cli-profile-{target}"  # Dynamique ✅
    dbt_cli_profile = DbtCliProfile.load(profile_block_name)
```

**Pourquoi ?** 
- ✅ Flexibilité : Un seul code pour dev ET prod
- ✅ Évolutivité : Facile d'ajouter staging, test, etc.
- ✅ Convention : Suit le pattern de nommage défini dans `flows.py`

#### B) Chargement Dynamique des Blocs

**Le Pattern** :
```python
# 1. Construction du nom selon la convention
profile_block_name = f"dbt-cli-profile-{target}"
# Si target="dev"  → "dbt-cli-profile-dev"
# Si target="prod" → "dbt-cli-profile-prod"

# 2. Chargement du bloc depuis Prefect
dbt_cli_profile = DbtCliProfile.load(profile_block_name)
```

**Ce qui se passe en coulisses** :
1. Prefect contacte son API (local ou cloud)
2. Récupère le bloc avec ce nom
3. Le bloc contient toute la config : projet GCP, dataset, credentials, threads
4. Le profil est prêt à être utilisé par dbt

#### C) Gestion d'Erreur Explicite

**Ajout de try/except** :
```python
try:
    dbt_cli_profile = DbtCliProfile.load(profile_block_name)
    logger.info(f"✅ Profil chargé: {dbt_cli_profile.name}")
except ValueError as e:
    logger.error(f"❌ Impossible de charger le bloc '{profile_block_name}'")
    logger.error("Assurez-vous d'avoir exécuté le setup")
    raise ValueError("Instructions détaillées...") from e
```

**Pourquoi ?**
- ✅ UX : Messages d'erreur clairs pour l'utilisateur
- ✅ Debug : Indique exactement quoi faire en cas de problème
- ✅ Robustesse : Évite des erreurs cryptiques

#### D) Propagation du Paramètre

**Modification du flow principal** :
```python
@flow(name="pipeline-dbt-complet")
def dbt_full_pipeline(target: str = "dev"):
    # Le paramètre est propagé à toutes les tâches
    run_result = run_dbt_models(target=target)
    test_result = test_dbt_models(target=target)
    
    return {
        "target": target,  # On retourne aussi le target utilisé
        "run": run_result,
        "test": test_result,
    }
```

## 🧠 Concepts et Logique

### 1. Separation of Concerns (Séparation des Responsabilités)

**Principe** : Chaque partie du code a une responsabilité unique et bien définie.

| Module | Responsabilité | Fréquence |
|--------|----------------|-----------|
| `infrastructure/setup_profiles/` | **Configuration** : Crée les blocs | Une fois |
| `prefect_flows/pipeline.py` | **Exécution** : Utilise les blocs | Souvent |

**Avantages** :
- ✅ Maintenabilité : Changement de config ? Modifiez seulement setup
- ✅ Testabilité : On peut tester setup et pipeline séparément
- ✅ Clarté : Chaque fichier a un rôle clair

### 2. Dependency Injection (Injection de Dépendances)

**Concept** : Au lieu de créer les objets dont on a besoin, on les **injecte** de l'extérieur.

**Avant (création inline)** :
```python
def run_dbt_models():
    # On crée tout nous-mêmes
    credentials = GcpCredentials(project=..., service_account_info=...)
    target_configs = BigQueryTargetConfigs(...)
    dbt_cli_profile = DbtCliProfile(...)
    # Beaucoup de code dupliqué !
```

**Après (injection via blocs)** :
```python
def run_dbt_models(target: str = "dev"):
    # On charge un objet pré-configuré
    dbt_cli_profile = DbtCliProfile.load(f"dbt-cli-profile-{target}")
    # Simple et réutilisable !
```

**Avantages** :
- ✅ DRY (Don't Repeat Yourself)
- ✅ Configuration centralisée
- ✅ Moins de code = moins de bugs

### 3. Configuration as Code

**Principe** : La configuration est du code versionné, pas des fichiers manuels.

**Flow de configuration** :
```
1. Terraform → Crée ressources GCP
2. setup_profiles → Lit outputs Terraform
3. setup_profiles → Crée blocs Prefect
4. pipeline.py → Utilise les blocs
```

**Avantages** :
- ✅ Versionning : Git track les changements
- ✅ Reproductibilité : Même config = même résultat
- ✅ Automatisation : Pas de configuration manuelle

### 4. Environment Parameterization (Paramétrisation d'Environnement)

**Pattern** : Un seul code, plusieurs environnements via paramètres.

**Implémentation** :
```python
# DEV
dbt_full_pipeline(target="dev")
# → Charge dbt-cli-profile-dev
# → Dataset dev, 1 thread

# PROD  
dbt_full_pipeline(target="prod")
# → Charge dbt-cli-profile-prod
# → Dataset prod, 4 threads
```

**Avantages** :
- ✅ Pas de duplication de code (pas de pipeline_dev.py et pipeline_prod.py)
- ✅ Cohérence entre environnements
- ✅ Facilité d'ajout d'environnements (staging, test, etc.)

### 5. Fail-Fast avec Messages Explicites

**Principe** : Échouer rapidement avec des messages clairs plutôt que continuer avec une erreur cachée.

**Implémentation** :
```python
try:
    dbt_cli_profile = DbtCliProfile.load(profile_block_name)
except ValueError as e:
    # Message explicite
    logger.error(f"❌ Bloc '{profile_block_name}' introuvable")
    logger.error("Commande à exécuter :")
    logger.error("  uv run python -m infrastructure.setup_profiles")
    # Raise avec contexte
    raise ValueError("Message détaillé...") from e
```

**Avantages** :
- ✅ Debug facile : L'erreur dit exactement quoi faire
- ✅ UX développeur : Pas besoin de deviner
- ✅ Documentation inline : Le code enseigne son utilisation

### 6. Retry Strategy pour la Résilience

**Pattern** : Réessayer automatiquement en cas d'échec temporaire.

**Implémentation** :
```python
@task(name="dbt-run", retries=2, retry_delay_seconds=30)
def run_dbt_models(target: str = "dev"):
    # Si ça échoue, Prefect réessaie 2 fois avec 30s d'attente
```

**Pourquoi ?**
- BigQuery peut avoir des **rate limits** temporaires
- Les connexions réseau peuvent être **instables**
- Les requêtes complexes peuvent **timeout** occasionnellement

**Stratégie** :
- Run : 2 retries (total 3 tentatives) avec 30s d'attente
- Test : 1 retry (total 2 tentatives) car moins critique

## 🔄 Flux d'Exécution Complet

### Setup Initial (Une fois)

```bash
# 1. Créer l'infrastructure GCP
cd infrastructure
terraform apply
terraform output -json > terraform-outputs.json

# 2. Créer les blocs Prefect
cd ..
uv run python -m infrastructure.setup_profiles
```

**Ce qui est créé** :
```
Prefect Blocks créés :
├── gcp-credentials
├── bigquery-target-configs-dev
├── bigquery-target-configs-prod
├── dbt-cli-profile-dev
│   ├── name: "projet_m2_bi"
│   ├── target: "dev"
│   ├── dataset: "decisive_plasma_473714_i8_dev"
│   ├── threads: 1
│   └── credentials: → gcp-credentials
└── dbt-cli-profile-prod
    ├── name: "projet_m2_bi"
    ├── target: "prod"
    ├── dataset: "decisive_plasma_473714_i8_prod"
    ├── threads: 4
    └── credentials: → gcp-credentials
```

### Exécution de la Pipeline (À chaque run)

```bash
# Exécuter sur dev
uv run python prefect_flows/pipeline.py
```

**Ce qui se passe** :

1. **Démarrage du flow** : `dbt_full_pipeline(target="dev")`

2. **Tâche 1 - run_dbt_models** :
   ```
   a. Construction du nom : "dbt-cli-profile-dev"
   b. Chargement du bloc depuis Prefect
   c. Le bloc contient toute la config
   d. Exécution de "dbt run" avec cette config
   e. Si échec → Retry (2x max)
   ```

3. **Tâche 2 - test_dbt_models** :
   ```
   a. Construction du nom : "dbt-cli-profile-dev"
   b. Chargement du bloc depuis Prefect
   c. Exécution de "dbt test" avec cette config
   d. Si échec → Retry (1x max)
   ```

4. **Retour du résultat** :
   ```json
   {
     "target": "dev",
     "run": <résultat dbt run>,
     "test": <résultat dbt test>
   }
   ```

## 📊 Comparaison Avant/Après

### Avant

**Problèmes** :
- ❌ Profil hardcodé inexistant
- ❌ Impossible de changer d'environnement
- ❌ Configuration dupliquée
- ❌ Pas de gestion d'erreur
- ❌ Code couplé à un seul environnement

### Après

**Améliorations** :
- ✅ Chargement dynamique des blocs Prefect
- ✅ Paramètre `target` pour choisir l'environnement
- ✅ Configuration centralisée dans les blocs
- ✅ Gestion d'erreur explicite
- ✅ Code découplé et réutilisable

## 🚀 Utilisation Pratique

### Développement Local

```bash
# Tester sur dev
uv run python prefect_flows/pipeline.py

# Pour tester sur prod, modifier dans pipeline.py :
# dbt_full_pipeline(target="prod")
```

### Avec Prefect Cloud

```bash
# Créer un deployment pour dev
prefect deployment build prefect_flows/pipeline.py:dbt_full_pipeline \
  -n "dbt-dev" \
  --param target=dev

# Créer un deployment pour prod
prefect deployment build prefect_flows/pipeline.py:dbt_full_pipeline \
  -n "dbt-prod" \
  --param target=prod

# Appliquer les deployments
prefect deployment apply dbt_full_pipeline-deployment.yaml

# Exécuter
prefect deployment run pipeline-dbt-complet/dbt-dev
prefect deployment run pipeline-dbt-complet/dbt-prod

# Scheduler (tous les jours à 2h du matin)
prefect deployment schedule create pipeline-dbt-complet/dbt-prod \
  --cron "0 2 * * *"
```

## 🎓 Leçons Clés

### 1. Séparation Setup vs Exécution
**Setup** crée la configuration, **Exécution** l'utilise. Cela permet de changer la config sans toucher au code d'exécution.

### 2. Convention de Nommage
`dbt-cli-profile-{target}` est une convention. Respecter les conventions rend le code prévisible.

### 3. Paramètres par Défaut
`target: str = "dev"` signifie que dev est l'environnement par défaut. Pratique pour le développement local.

### 4. Gestion d'Erreur Préventive
Mieux vaut un message clair qui dit "Exécutez cette commande" qu'une stack trace cryptique.

### 5. Documentation dans le Code
Les docstrings détaillées et les commentaires expliquent le "pourquoi", pas juste le "quoi".

## 🔮 Prochaines Étapes

Maintenant que la pipeline est configurée, vous pouvez :

1. **Développer vos modèles dbt** dans `dbt/models/`
2. **Tester localement** : `cd dbt && dbt run --target dev`
3. **Exécuter via Prefect** : `uv run python prefect_flows/pipeline.py`
4. **Ajouter d'autres tâches** : docs, snapshots, seeds, etc.
5. **Configurer le monitoring** : alertes, métriques, logs
6. **Déployer sur Prefect Cloud** : scheduling, UI, collaboration

## 📚 Résumé des Fichiers Modifiés

| Fichier | Modification | Raison |
|---------|-------------|--------|
| `prefect_flows/pipeline.py` | Ajout paramètre `target` | Flexibilité dev/prod |
| `prefect_flows/pipeline.py` | Chargement dynamique blocs | Utiliser setup existant |
| `prefect_flows/pipeline.py` | Gestion d'erreur | UX et robustesse |
| `prefect_flows/pipeline.py` | Import `get_run_logger` | Meilleur logging |
| `prefect_flows/README.md` | Création | Documentation |
| `documentation/explication_pipeline_prefect.md` | Création | Concepts et apprentissage |

