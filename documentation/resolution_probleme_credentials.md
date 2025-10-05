# Résolution du Problème d'Authentification dbt

## 🐛 Problème Rencontré

Lors de l'exécution de la pipeline, l'erreur suivante est apparue :

```
Runtime Error
  Credentials in profile "projet_m2_bi", target "dev" invalid: Runtime Error
    Must specify authentication method
```

## 🔍 Diagnostic

### Cause Racine

Le fichier `dbt/profiles.yml` contenait un **chemin incorrect** vers le fichier de service account :

```yaml
keyfile: "/home/bafbi/school/m2/bi/projet-m2-bi/.secrets/sa_key.json"  # ❌ Mauvais chemin (Linux)
```

Ce chemin provenait d'une autre machine (Linux), alors que l'utilisateur est sur macOS avec un chemin différent.

### Problème Secondaire

Le code utilisait `overwrite_profiles=True` avec `DbtCoreOperation`, ce qui créait des conflits entre :
- Les blocs Prefect (qui stockent `service_account_info` comme JSON string)
- dbt (qui attend un chemin vers un fichier `keyfile`)

Quand Prefect-dbt génère un `profiles.yml` depuis les blocs, il ne sait pas comment convertir `service_account_info` en un chemin de fichier.

## ✅ Solution Implémentée

### 1. Régénération du `profiles.yml` Local

**Commande** :
```bash
uv run python -m infrastructure.setup_profiles --local-only
```

**Résultat** : Le `profiles.yml` a été régénéré avec le bon chemin :
```yaml
keyfile: "/Users/mac-CKELMA23/Documents/projects/projet-m2-bi/.secrets/sa_key.json"  # ✅ Bon chemin (macOS)
```

### 2. Modification de `pipeline.py`

**Changement Principal** : Utilisation du `profiles.yml` local au lieu des blocs Prefect.

#### Avant (ne fonctionnait pas)

```python
@task(name="dbt-run")
def run_dbt_models(target: str = "dev"):
    # Charge le profil depuis les blocs Prefect
    profile_block_name = f"dbt-cli-profile-{target}"
    dbt_cli_profile = DbtCliProfile.load(profile_block_name)
    
    # Tente d'écraser profiles.yml avec le contenu du bloc
    result = DbtCoreOperation(
        commands=["dbt run"],
        project_dir=str(project_dir),
        overwrite_profiles=True,  # ❌ Problème ici
        dbt_cli_profile=dbt_cli_profile,
    ).run()
```

**Problème** : `overwrite_profiles=True` génère un `profiles.yml` qui ne fonctionne pas car les blocs Prefect stockent les credentials différemment de ce que dbt attend.

#### Après (fonctionne)

```python
@task(name="dbt-run")
def run_dbt_models(target: str = "dev"):
    project_dir = Path(__file__).parent.parent / "dbt"
    profiles_dir = project_dir
    
    # Vérifie que profiles.yml existe
    if not (profiles_dir / "profiles.yml").exists():
        raise FileNotFoundError("Exécutez: uv run python -m infrastructure.setup_profiles --local-only")
    
    # Utilise le profiles.yml local
    result = DbtCoreOperation(
        commands=[f"dbt run --target {target}"],
        project_dir=str(project_dir),
        profiles_dir=str(profiles_dir),
        overwrite_profiles=False,  # ✅ Utilise le fichier local
    ).run()
```

**Avantages** :
- ✅ Utilise le `profiles.yml` local généré correctement
- ✅ Pas de conflit entre blocs Prefect et dbt
- ✅ Plus simple et plus fiable
- ✅ Le paramètre `--target {target}` permet de choisir dev/prod

## 🎓 Concepts Techniques

### 1. Différence entre `service_account_info` et `keyfile`

**`service_account_info`** (Prefect GcpCredentials) :
- Contient le **contenu JSON** du service account
- Stocké comme une chaîne de caractères
- Utilisé par les bibliothèques Python Google Cloud directement

**`keyfile`** (dbt BigQuery) :
- Contient le **chemin vers un fichier** JSON
- dbt lit ce fichier au runtime
- Format attendu par dbt : `keyfile: "/path/to/sa_key.json"`

### 2. Problème avec `overwrite_profiles=True`

Quand `overwrite_profiles=True` :
1. Prefect-dbt génère un `profiles.yml` temporaire
2. Il essaie de convertir `service_account_info` en configuration dbt
3. La conversion ne fonctionne pas toujours correctement
4. dbt ne peut pas s'authentifier

### 3. Solution : Séparation des Responsabilités

**Génération de configuration** (une fois) :
```bash
uv run python -m infrastructure.setup_profiles --local-only
```
→ Crée un `profiles.yml` correct avec les bons chemins

**Exécution** (à chaque run) :
```bash
uv run python prefect_flows/pipeline.py
```
→ Utilise le `profiles.yml` existant (pas de génération dynamique)

## 🔄 Workflow Mis à Jour

### Setup Initial (Une fois)

```bash
# 1. Infrastructure GCP
cd infrastructure
terraform apply
terraform output -json > terraform-outputs.json

# 2. Générer profiles.yml local
cd ..
uv run python -m infrastructure.setup_profiles --local-only
```

### Développement (À chaque fois)

```bash
# Exécuter la pipeline
uv run python prefect_flows/pipeline.py

# Ou tester dbt directement
cd dbt && dbt run --target dev
```

### Changement d'Environnement

Le `profiles.yml` contient **à la fois** dev et prod :

```yaml
projet_m2_bi:
  target: dev  # Target par défaut
  outputs:
    dev:
      # Config dev
    prod:
      # Config prod
```

Pour changer d'environnement :
1. **Option 1** : Modifier `target: dev` → `target: prod` dans `profiles.yml`
2. **Option 2** : Utiliser `--target` en ligne de commande : `dbt run --target prod`
3. **Option 3** : Modifier `pipeline.py` : `dbt_full_pipeline(target="prod")`

## 📊 Résultat Final

```
✅ 2 modèles dbt créés dans BigQuery
   - my_first_dbt_model (table)
   - my_second_dbt_model (view)

✅ 2 tests passés
   - unique_my_first_dbt_model_id
   - unique_my_second_dbt_model_id

✅ Pipeline complète en ~12 secondes
```

## 🚀 Prochaines Étapes

Maintenant que la pipeline fonctionne, vous pouvez :

1. **Créer vos propres modèles dbt** dans `dbt/models/`
2. **Ajouter des sources** dans `dbt/models/sources.yml`
3. **Créer des tests custom**
4. **Ajouter des snapshots** pour capturer l'historique
5. **Générer la documentation** : `cd dbt && dbt docs generate && dbt docs serve`

## 💡 Leçons Apprises

### 1. Chemins Absolus vs Relatifs

**Problème** : Les chemins absolus dans les fichiers de configuration ne fonctionnent pas entre machines différentes.

**Solution** : 
- Générer `profiles.yml` localement sur chaque machine
- Utiliser des chemins relatifs quand possible
- Automatiser la génération avec des scripts

### 2. Abstraction vs Simplicité

**Tentative initiale** : Utiliser les blocs Prefect pour tout (configuration centralisée)

**Réalité** : Parfois, un fichier local simple (`profiles.yml`) est plus fiable qu'une abstraction complexe.

**Compromis** :
- Blocs Prefect pour Prefect Cloud (déploiements, scheduling)
- `profiles.yml` local pour le développement local

### 3. Fail-Fast avec Messages Clairs

Le nouveau code vérifie que `profiles.yml` existe avant d'exécuter :

```python
if not (profiles_dir / "profiles.yml").exists():
    raise FileNotFoundError("Exécutez: uv run python -m infrastructure.setup_profiles --local-only")
```

**Avantage** : L'erreur dit exactement quoi faire, pas besoin de deviner.

## 📚 Ressources

- [dbt BigQuery Setup](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [Prefect Blocks](https://docs.prefect.io/concepts/blocks/)

