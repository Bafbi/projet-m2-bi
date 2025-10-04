# Flows Prefect - Projet M2 BI

Ce dossier contient les flows Prefect pour orchestrer les transformations dbt du projet M2 BI. Le flow charge automatiquement les credentials GCP depuis un Block Prefect, éliminant le besoin de fichiers de clés locaux en production.

## Table des matières

- [Prérequis](#prérequis)
- [Configuration locale (développement)](#configuration-locale-développement)
- [Configuration Prefect Cloud (production)](#configuration-prefect-cloud-production)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Variables d'environnement](#variables-denvironnement)
- [Ressources](#ressources)

---

## Prérequis

- Python 3.9+
- Accès à un projet GCP avec BigQuery
- Infrastructure provisionnée via Terraform (datasets, service account)
- Fichier `infrastructure/terraform-outputs.json` disponible

## Configuration locale (développement)

### Étape 1 : Installation des dépendances

```bash
# Depuis la racine du projet
pip install -r requirements.txt
```

### Étape 2 : Génération du fichier .env

Le fichier `.env` contient les variables d'environnement nécessaires au flow Prefect. Il est généré automatiquement depuis les outputs Terraform.

```bash
# Générer .env depuis terraform-outputs.json
python utilities/generate_env.py
```

Le script crée un fichier `.env` à la racine du projet avec les valeurs suivantes :
- `PREFECT_GCP_CREDENTIALS_BLOCK` : nom du Block Prefect (par défaut : `sa-key`)
- `DBT_TARGET` : environnement cible (`dev` en local)
- `DBT_BIGQUERY_DATASET_DEV` : dataset BigQuery de développement
- `DBT_BIGQUERY_DATASET_PROD` : dataset BigQuery de production
- `DBT_PROFILE_NAME` : nom du profil dbt (par défaut : `projet_m2_bi`)

**Options avancées** :
```bash
# Prévisualiser sans créer le fichier
python utilities/generate_env.py --dry-run

# Utiliser un fichier d'outputs personnalisé
python utilities/generate_env.py --outputs-json chemin/custom.json

# Spécifier un nom de block différent
python utilities/generate_env.py --block-name mon-block-gcp
```

### Étape 3 : Création du Block GCP Credentials

Le Block Prefect stocke les credentials GCP de manière sécurisée. À créer une seule fois en local.

```bash
python -c "
from prefect_gcp.credentials import GcpCredentials
import json

with open('.secrets/sa_key.json') as f:
    credentials = GcpCredentials(service_account_info=json.load(f))

credentials.save('sa-key', overwrite=True)
print('Block GCP créé avec succès : sa-key')
"
```

Le Block est stocké localement dans `~/.prefect/prefect.db`.

### Étape 4 : Tester le flow localement

```bash
python prefect/pipeline.py
```

Vous devriez voir :
```
======================================================================
CONFIGURATION DBT PROFILE
======================================================================
Block GCP        : sa-key
Target           : dev
Dataset utilisé  : <votre_dataset_dev>
Nom du profil    : projet_m2_bi
======================================================================
Démarrage de la pipeline...
```

---

## Configuration Prefect Cloud (production)

### Étape 1 : Authentification à Prefect Cloud

```bash
prefect-cloud login
```

Suivez les instructions pour vous authentifier via votre navigateur.

### Étape 2 : Création du Block GCP Credentials dans Prefect Cloud

**IMPORTANT** : Le Block doit être créé dans Prefect Cloud avant le déploiement.

**Option A - Via Python (depuis votre machine locale)** :
```bash
python -c "
from prefect_gcp.credentials import GcpCredentials
import json

with open('.secrets/sa_key.json') as f:
    credentials = GcpCredentials(service_account_info=json.load(f))

credentials.save('sa-key', overwrite=True)
print('Block GCP créé dans Prefect Cloud : sa-key')
"
```

**Option B - Via l'interface web Prefect Cloud** :
1. Connectez-vous à Prefect Cloud
2. Allez dans **Blocks** → **Add Block** → **GCP Credentials**
3. Nom du block : `sa-key`
4. Collez le contenu JSON de votre service account key
5. Cliquez sur **Create**

### Étape 3 : Configuration des variables d'environnement

Les variables d'environnement doivent être configurées manuellement dans Prefect Cloud. Elles ne sont pas incluses dans le déploiement du code.

**Via l'interface web** :
1. Allez dans **Variables**
2. Créez les variables suivantes :

| Nom de la variable | Valeur | Description |
|-------------------|--------|-------------|
| `PREFECT_GCP_CREDENTIALS_BLOCK` | `sa-key` | Nom du Block GCP créé précédemment |
| `DBT_TARGET` | `prod` | **CRITIQUE** : spécifie l'environnement production |
| `DBT_BIGQUERY_DATASET_DEV` | `<votre_dataset_dev>` | Dataset BigQuery de développement |
| `DBT_BIGQUERY_DATASET_PROD` | `<votre_dataset_prod>` | Dataset BigQuery de production |
| `DBT_PROFILE_NAME` | `projet_m2_bi` | Nom du profil dbt (optionnel) |

**Via CLI** :
```bash
prefect variable set PREFECT_GCP_CREDENTIALS_BLOCK sa-key
prefect variable set DBT_TARGET prod
prefect variable set DBT_BIGQUERY_DATASET_DEV test_terraform_473818_dev
prefect variable set DBT_BIGQUERY_DATASET_PROD test_terraform_473818_prod
prefect variable set DBT_PROFILE_NAME projet_m2_bi
```

**ATTENTION** : La variable `DBT_TARGET` est critique. Si elle n'est pas définie à `prod`, le flow utilisera la valeur par défaut `dev` et écrira dans le dataset de développement depuis l'environnement de production.

### Étape 4 : Vérification de la configuration

Vérifiez que les variables sont correctement configurées :

```bash
# Vérifier une variable spécifique
prefect variable get DBT_TARGET
# Résultat attendu : prod

# Lister toutes les variables
prefect variable ls
```

### Étape 5 : Déploiement du flow

```bash
# Déployer le flow sur Prefect Cloud
prefect-cloud deploy prefect/pipeline.py:dbt_full_pipeline

# Vérifier les déploiements
prefect-cloud ls
```

### Étape 6 : Exécution et planification

**Exécution manuelle** :
```bash
prefect-cloud run pipeline-dbt-complet
```

**Planification récurrente** :
```bash
# Exécution quotidienne à 9h
prefect-cloud schedule pipeline-dbt-complet --cron "0 9 * * *"

# Autres exemples de cron :
# Toutes les 4 heures : "0 */4 * * *"
# Tous les lundis à 9h : "0 9 * * 1"
# Le 1er du mois à minuit : "0 0 1 * *"
```

---

## Utilisation

### Exécution locale

Après avoir complété la configuration locale :

```bash
python prefect/pipeline.py
```

Le flow effectue les opérations suivantes :
1. Charge les variables d'environnement depuis `.env`
2. Construit un profil dbt depuis le Block GCP
3. Exécute `dbt run` (transformations)
4. Exécute `dbt test` (tests de qualité)

### Tester dbt directement (sans Prefect)

Si vous souhaitez tester les modèles dbt indépendamment de Prefect :

```bash
cd dbt
dbt run --profiles-dir . --profile projet_m2_bi
dbt test --profiles-dir . --profile projet_m2_bi
```

Cette approche utilise le fichier `profiles.yml` avec les credentials locaux. Elle est utile pour le développement rapide de modèles dbt.

---

## Architecture

### Vue d'ensemble du workflow

```
Infrastructure Terraform
         |
         | tofu output -json
         v
terraform-outputs.json  (source de vérité : datasets, projet, région)
         |
         | python utilities/generate_env.py
         v
     .env (local)
         |
         | load_dotenv() au démarrage
         v
Variables d'environnement disponibles
         |
         | os.getenv()
         v
GcpCredentials.load() + BigQueryTargetConfigs
         |
         | Construit DbtCliProfile en mémoire
         v
DbtCoreOperation (overwrite_profiles=True)
         |
         v
   dbt run / dbt test
         |
         v
    BigQuery
```

### Séparation des environnements

**Environnement local (développement)** :
- Variables : fichier `.env` généré automatiquement
- Block GCP : stocké dans `~/.prefect/prefect.db`
- Target dbt : `dev` (par défaut)
- Dataset : dataset de développement

**Environnement cloud (production)** :
- Variables : configurées manuellement dans l'UI Prefect Cloud
- Block GCP : stocké de manière chiffrée dans Prefect Cloud
- Target dbt : `prod` (à configurer explicitement)
- Dataset : dataset de production

### Pourquoi des Blocks Prefect ?

**Problème avec l'approche traditionnelle** (fichier `profiles.yml` + clé sur disque) :
- Fichier de clé requis sur chaque runner
- Risque de commit accidentel
- Rotation de clés complexe
- Gestion manuelle des secrets en production

**Solution avec Blocks Prefect** :
- Credentials stockés de manière chiffrée dans Prefect
- Pas de fichiers secrets sur le filesystem des runners
- Rotation facile via l'UI
- Audit complet des accès
- Même code pour local et cloud

### Flux de données

1. **Terraform** : provisionne l'infrastructure GCP et exporte les outputs
2. **generate_env.py** : parse les outputs Terraform et génère `.env`
3. **python-dotenv** : charge `.env` au démarrage du flow (local uniquement)
4. **os.getenv()** : récupère les variables (depuis `.env` local ou variables Prefect Cloud)
5. **GcpCredentials.load()** : charge le Block depuis Prefect (local ou cloud)
6. **DbtCliProfile** : construit un profil dbt en mémoire avec les credentials du Block
7. **DbtCoreOperation** : exécute dbt avec le profil injecté (ignore `profiles.yml`)
8. **BigQuery** : reçoit les requêtes dbt et exécute les transformations

---

## Variables d'environnement

| Variable | Défaut | Description | Environnement |
|----------|--------|-------------|---------------|
| `PREFECT_GCP_CREDENTIALS_BLOCK` | `sa-key` | Nom du Block Prefect GCP Credentials | Local + Cloud |
| `DBT_TARGET` | `dev` | Cible dbt : `dev` ou `prod` | **Local : `dev` / Cloud : `prod`** |
| `DBT_BIGQUERY_DATASET_DEV` | (Terraform) | Dataset BigQuery de développement | Local + Cloud |
| `DBT_BIGQUERY_DATASET_PROD` | (Terraform) | Dataset BigQuery de production | Local + Cloud |
| `DBT_PROFILE_NAME` | `projet_m2_bi` | Nom du profil dbt | Local + Cloud (optionnel) |

**Convention importante** :
- En local : `DBT_TARGET=dev` (défini automatiquement par `generate_env.py`)
- En production : `DBT_TARGET=prod` (à configurer manuellement dans Prefect Cloud)

Le flow utilise la valeur de `DBT_TARGET` pour sélectionner le dataset approprié :
- Si `DBT_TARGET=dev` → utilise `DBT_BIGQUERY_DATASET_DEV`
- Si `DBT_TARGET=prod` → utilise `DBT_BIGQUERY_DATASET_PROD`

---

## Ressources

- [Prefect Documentation](https://docs.prefect.io/)
- [prefect-gcp](https://prefecthq.github.io/prefect-gcp/)
- [prefect-dbt](https://prefecthq.github.io/prefect-dbt/)
- [dbt Core](https://docs.getdbt.com/)
- [BigQuery Credentials](https://cloud.google.com/bigquery/docs/authentication)
