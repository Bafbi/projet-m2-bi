# 🚀 Guide de Démarrage Rapide - Pipeline dbt + Prefect

## 📋 Étapes de Configuration (À faire une fois)

### 1. Setup de l'Infrastructure GCP

```bash
cd infrastructure
terraform apply
terraform output -json > terraform-outputs.json
cd ..
```

### 2. Setup des Blocs Prefect

```bash
# Configuration complète (profiles locaux + blocs Prefect)
uv run python -m infrastructure.setup_profiles

# OU seulement les blocs Prefect (si profiles.yml existe déjà)
uv run python -m infrastructure.setup_profiles --blocks-only
```

✅ **Vérification** : Vous devriez voir dans les logs :
- `gcp-credentials` créé
- `dbt-cli-profile-dev` créé
- `dbt-cli-profile-prod` créé

## 🏃 Exécution de la Pipeline

### Développement Local (Environnement Dev)

```bash
# Exécuter la pipeline sur l'environnement dev
uv run python prefect_flows/pipeline.py
```

### Pour Tester sur Prod

Modifier dans `prefect_flows/pipeline.py` :
```python
if __name__ == "__main__":
    dbt_full_pipeline(target="prod")  # Changer "dev" en "prod"
```

Puis exécuter :
```bash
uv run python prefect_flows/pipeline.py
```

## 🔍 Résolution de Problèmes

### Erreur : "Le bloc Prefect 'dbt-cli-profile-dev' n'existe pas"

**Solution** : Exécuter le setup des blocs :
```bash
uv run python -m infrastructure.setup_profiles
```

### Erreur : "terraform-outputs.json introuvable"

**Solution** : Générer les outputs Terraform :
```bash
cd infrastructure
terraform output -json > terraform-outputs.json
cd ..
```

### Erreur : "Service account file not found"

**Solution** : Placer votre clé de service account dans :
```bash
.secrets/sa_key.json
```

## 📊 Développement de Modèles dbt

### 1. Créer un Nouveau Modèle

```bash
# Dans dbt/models/
touch dbt/models/mon_modele.sql
```

### 2. Tester Localement avec dbt

```bash
cd dbt

# Run un modèle spécifique
dbt run --select mon_modele --target dev

# Tester un modèle
dbt test --select mon_modele --target dev
```

### 3. Exécuter via la Pipeline Prefect

```bash
cd ..
uv run python prefect_flows/pipeline.py
```

## 🎯 Workflows Courants

### Workflow de Développement

```bash
# 1. Créer/modifier un modèle dans dbt/models/
# 2. Tester localement
cd dbt && dbt run --select mon_modele --target dev

# 3. Exécuter la pipeline complète
cd .. && uv run python prefect_flows/pipeline.py
```

### Workflow de Déploiement en Prod

```bash
# 1. Tester sur dev
uv run python prefect_flows/pipeline.py  # (avec target="dev")

# 2. Si OK, modifier pour prod
# Changer target="prod" dans pipeline.py

# 3. Exécuter sur prod
uv run python prefect_flows/pipeline.py
```

## 📚 Structure des Fichiers

```
projet-m2-bi/
├── infrastructure/
│   ├── main.tf                    # Infrastructure GCP
│   ├── terraform-outputs.json     # Outputs Terraform (généré)
│   └── setup_profiles/
│       ├── flows.py               # Setup des blocs Prefect
│       └── tasks.py               # Tâches de setup
├── dbt/
│   ├── dbt_project.yml           # Config dbt
│   ├── profiles.yml              # Profils dbt (généré)
│   └── models/                   # Vos modèles dbt
│       └── example/
│           ├── my_first_dbt_model.sql
│           └── my_second_dbt_model.sql
├── prefect_flows/
│   ├── pipeline.py               # Pipeline principale ⭐
│   ├── pipeline_extended_example.py  # Exemples d'extensions
│   └── README.md                 # Documentation
└── documentation/
    └── explication_pipeline_prefect.md  # Concepts détaillés
```

## 🔄 Cycle de Vie

```
┌─────────────────────────────────────────┐
│  SETUP (Une fois ou lors de changement) │
├─────────────────────────────────────────┤
│  1. terraform apply                      │
│  2. terraform output -json > ...         │
│  3. python -m infrastructure.setup_profiles │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  DÉVELOPPEMENT (Itératif)                │
├─────────────────────────────────────────┤
│  1. Créer/modifier modèles dbt           │
│  2. Tester : dbt run --select ...        │
│  3. Valider : python pipeline.py         │
│  4. Répéter                              │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  PRODUCTION (Quotidien/Schedulé)         │
├─────────────────────────────────────────┤
│  • Exécution automatique via Prefect    │
│  • Monitoring des runs                   │
│  • Alertes en cas d'échec                │
└─────────────────────────────────────────┘
```

## ✨ Commandes Utiles

### dbt

```bash
cd dbt

# Run tous les modèles
dbt run --target dev

# Run un modèle spécifique
dbt run --select mon_modele --target dev

# Run un tag
dbt run --select tag:daily --target dev

# Tester
dbt test --target dev

# Générer la documentation
dbt docs generate
dbt docs serve  # Ouvre un navigateur
```

### Prefect

```bash
# Lister les blocs
prefect block ls

# Voir les runs
prefect flow-run ls

# Voir les logs d'un run
prefect flow-run logs <run-id>
```

### Terraform

```bash
cd infrastructure

# Voir les outputs
terraform output

# Régénérer le fichier JSON
terraform output -json > terraform-outputs.json

# Appliquer des changements
terraform apply
```

## 🎓 Ressources

- **Documentation du projet** : `documentation/explication_pipeline_prefect.md`
- **Exemples d'extensions** : `prefect_flows/pipeline_extended_example.py`
- **README Prefect** : `prefect_flows/README.md`
- **README Infrastructure** : `infrastructure/README.md`

## 💡 Prochaines Étapes

1. ✅ Setup terminé
2. ✅ Pipeline configurée
3. 🚀 **MAINTENANT** : Créer vos modèles dbt dans `dbt/models/`
4. 📊 Développer votre data warehouse
5. 🔄 Automatiser avec Prefect Cloud (optionnel)

---

**Bon développement ! 🚀**

