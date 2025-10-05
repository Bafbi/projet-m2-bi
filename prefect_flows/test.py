"""
Exemple d'extension de la pipeline dbt avec des commandes supplémentaires

Ce fichier montre comment ajouter facilement de nouvelles tâches dbt
en suivant le même pattern que pipeline.py.

Pour l'utiliser, copiez les fonctions dont vous avez besoin dans pipeline.py
"""
from prefect import flow, task, get_run_logger
from prefect_dbt.cli.commands import DbtCoreOperation
from pathlib import Path
from prefect_dbt.cli import DbtCliProfile


@task(name="dbt-seed", retries=1)
def load_dbt_seeds(target: str = "dev"):
    """
    Charge les fichiers CSV seeds dans BigQuery (dbt seed)
    
    Les seeds sont des fichiers CSV dans dbt/seeds/ qui sont chargés
    comme des tables dans votre data warehouse. Utiles pour des
    données de référence (pays, catégories, etc.)
    
    Args:
        target: Environnement cible (dev ou prod)
    
    Returns:
        Résultat de l'exécution dbt seed
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profile_block_name = f"dbt-cli-profile-{target}"
    
    logger.info(f"Chargement des seeds depuis le bloc: {profile_block_name}")
    
    try:
        dbt_cli_profile = DbtCliProfile.load(profile_block_name)
        logger.info(f"✅ Profil chargé pour les seeds")
    except ValueError as e:
        logger.error(f"❌ Bloc '{profile_block_name}' introuvable")
        raise ValueError(
            f"Le bloc '{profile_block_name}' n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles"
        ) from e
    
    result = DbtCoreOperation(
        commands=["dbt seed"],
        project_dir=str(project_dir),
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
    ).run()
    
    return result


@task(name="dbt-docs-generate")
def generate_dbt_docs(target: str = "dev"):
    """
    Génère la documentation dbt (dbt docs generate)
    
    Crée un site web de documentation pour vos modèles dbt.
    La documentation inclut le lineage (dépendances entre modèles),
    les descriptions, les tests, etc.
    
    Args:
        target: Environnement cible (dev ou prod)
    
    Returns:
        Résultat de la génération de docs
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profile_block_name = f"dbt-cli-profile-{target}"
    
    logger.info(f"Génération de la documentation dbt...")
    
    try:
        dbt_cli_profile = DbtCliProfile.load(profile_block_name)
        logger.info(f"✅ Profil chargé pour la génération de docs")
    except ValueError as e:
        logger.error(f"❌ Bloc '{profile_block_name}' introuvable")
        raise ValueError(
            f"Le bloc '{profile_block_name}' n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles"
        ) from e
    
    result = DbtCoreOperation(
        commands=["dbt docs generate"],
        project_dir=str(project_dir),
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
    ).run()
    
    return result


@task(name="dbt-snapshot")
def run_dbt_snapshots(target: str = "dev"):
    """
    Exécute les snapshots dbt (dbt snapshot)
    
    Les snapshots permettent de capturer l'état d'une table à un moment donné
    (Type 2 Slowly Changing Dimensions). Utile pour tracker l'historique
    des changements dans vos données source.
    
    Args:
        target: Environnement cible (dev ou prod)
    
    Returns:
        Résultat de l'exécution des snapshots
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profile_block_name = f"dbt-cli-profile-{target}"
    
    logger.info(f"Exécution des snapshots dbt...")
    
    try:
        dbt_cli_profile = DbtCliProfile.load(profile_block_name)
        logger.info(f"✅ Profil chargé pour les snapshots")
    except ValueError as e:
        logger.error(f"❌ Bloc '{profile_block_name}' introuvable")
        raise ValueError(
            f"Le bloc '{profile_block_name}' n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles"
        ) from e
    
    result = DbtCoreOperation(
        commands=["dbt snapshot"],
        project_dir=str(project_dir),
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
    ).run()
    
    return result


@task(name="dbt-run-models-specific")
def run_specific_models(models: str, target: str = "dev"):
    """
    Exécute seulement certains modèles dbt (dbt run --select)
    
    Permet de ne run que certains modèles plutôt que tout le projet.
    Utile pour tester rapidement un modèle spécifique.
    
    Args:
        models: Sélection des modèles (ex: "my_model", "tag:daily", "path:marts/")
        target: Environnement cible (dev ou prod)
    
    Returns:
        Résultat de l'exécution
        
    Exemples:
        run_specific_models("my_model", target="dev")  # Un modèle
        run_specific_models("tag:daily", target="prod")  # Tous les modèles tagués "daily"
        run_specific_models("path:marts/", target="dev")  # Tous les modèles dans marts/
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profile_block_name = f"dbt-cli-profile-{target}"
    
    logger.info(f"Exécution des modèles sélectionnés: {models}")
    
    try:
        dbt_cli_profile = DbtCliProfile.load(profile_block_name)
        logger.info(f"✅ Profil chargé")
    except ValueError as e:
        logger.error(f"❌ Bloc '{profile_block_name}' introuvable")
        raise ValueError(
            f"Le bloc '{profile_block_name}' n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles"
        ) from e
    
    result = DbtCoreOperation(
        commands=[f"dbt run --select {models}"],
        project_dir=str(project_dir),
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
    ).run()
    
    return result


@task(name="dbt-freshness")
def check_source_freshness(target: str = "dev"):
    """
    Vérifie la fraîcheur des sources dbt (dbt source freshness)
    
    Vérifie si vos sources de données sont à jour selon les règles
    définies dans vos fichiers de sources (sources.yml).
    
    Args:
        target: Environnement cible (dev ou prod)
    
    Returns:
        Résultat de la vérification de fraîcheur
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profile_block_name = f"dbt-cli-profile-{target}"
    
    logger.info(f"Vérification de la fraîcheur des sources...")
    
    try:
        dbt_cli_profile = DbtCliProfile.load(profile_block_name)
        logger.info(f"✅ Profil chargé")
    except ValueError as e:
        logger.error(f"❌ Bloc '{profile_block_name}' introuvable")
        raise ValueError(
            f"Le bloc '{profile_block_name}' n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles"
        ) from e
    
    result = DbtCoreOperation(
        commands=["dbt source freshness"],
        project_dir=str(project_dir),
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
    ).run()
    
    return result


# ─────────────────────────────────────────────────────────────────
# EXEMPLES DE FLOWS COMPOSÉS
# ─────────────────────────────────────────────────────────────────


@flow(name="pipeline-dbt-complete-with-seeds", log_prints=True)
def dbt_pipeline_with_seeds(target: str = "dev"):
    """
    Pipeline complète incluant les seeds
    
    Ordre d'exécution :
    1. Load seeds (données de référence)
    2. Run models (transformations)
    3. Test models (qualité)
    """
    logger = get_run_logger()
    
    logger.info(f"🚀 Pipeline complète avec seeds (environnement: {target})")
    
    # 1. Charger les seeds
    logger.info("📥 Étape 1/3 : Chargement des seeds...")
    seed_result = load_dbt_seeds(target=target)
    
    # 2. Run les modèles
    logger.info("📊 Étape 2/3 : Exécution des modèles...")
    from prefect_flows.pipeline import run_dbt_models
    run_result = run_dbt_models(target=target)
    
    # 3. Tester
    logger.info("🧪 Étape 3/3 : Tests...")
    from prefect_flows.pipeline import test_dbt_models
    test_result = test_dbt_models(target=target)
    
    logger.info(f"✅ Pipeline avec seeds terminée !")
    
    return {
        "target": target,
        "seed": seed_result,
        "run": run_result,
        "test": test_result,
    }


@flow(name="pipeline-dbt-with-docs", log_prints=True)
def dbt_pipeline_with_documentation(target: str = "dev"):
    """
    Pipeline qui génère aussi la documentation
    
    Ordre d'exécution :
    1. Run models
    2. Test models
    3. Generate docs
    """
    logger = get_run_logger()
    
    logger.info(f"🚀 Pipeline avec documentation (environnement: {target})")
    
    # 1. Run
    logger.info("📊 Étape 1/3 : Exécution des modèles...")
    from prefect_flows.pipeline import run_dbt_models
    run_result = run_dbt_models(target=target)
    
    # 2. Test
    logger.info("🧪 Étape 2/3 : Tests...")
    from prefect_flows.pipeline import test_dbt_models
    test_result = test_dbt_models(target=target)
    
    # 3. Generate docs
    logger.info("📚 Étape 3/3 : Génération de la documentation...")
    docs_result = generate_dbt_docs(target=target)
    
    logger.info(f"✅ Pipeline avec documentation terminée !")
    logger.info(f"📖 Pour voir la documentation : cd dbt && dbt docs serve")
    
    return {
        "target": target,
        "run": run_result,
        "test": test_result,
        "docs": docs_result,
    }


@flow(name="pipeline-dbt-daily-with-snapshots", log_prints=True)
def dbt_daily_pipeline(target: str = "prod"):
    """
    Pipeline quotidienne de production
    
    Ordre d'exécution :
    1. Check source freshness (vérifier que les données sont à jour)
    2. Run snapshots (capturer l'historique)
    3. Run models (transformations)
    4. Test models (qualité)
    5. Generate docs (documentation)
    """
    logger = get_run_logger()
    
    logger.info(f"🚀 Pipeline quotidienne (environnement: {target})")
    
    # 1. Vérifier la fraîcheur des sources
    logger.info("🔍 Étape 1/5 : Vérification de la fraîcheur des sources...")
    freshness_result = check_source_freshness(target=target)
    
    # 2. Snapshots
    logger.info("📸 Étape 2/5 : Exécution des snapshots...")
    snapshot_result = run_dbt_snapshots(target=target)
    
    # 3. Run
    logger.info("📊 Étape 3/5 : Exécution des modèles...")
    from prefect_flows.pipeline import run_dbt_models
    run_result = run_dbt_models(target=target)
    
    # 4. Test
    logger.info("🧪 Étape 4/5 : Tests...")
    from prefect_flows.pipeline import test_dbt_models
    test_result = test_dbt_models(target=target)
    
    # 5. Docs
    logger.info("📚 Étape 5/5 : Génération de la documentation...")
    docs_result = generate_dbt_docs(target=target)
    
    logger.info(f"✅ Pipeline quotidienne terminée !")
    
    return {
        "target": target,
        "freshness": freshness_result,
        "snapshots": snapshot_result,
        "run": run_result,
        "test": test_result,
        "docs": docs_result,
    }


if __name__ == "__main__":
    """
    Exemples d'exécution
    """
    # Pipeline simple avec seeds
    # dbt_pipeline_with_seeds(target="dev")
    
    # Pipeline avec documentation
    # dbt_pipeline_with_documentation(target="dev")
    
    # Pipeline quotidienne complète (prod)
    # dbt_daily_pipeline(target="prod")
    
    # Run de modèles spécifiques
    # run_specific_models("my_first_dbt_model", target="dev")
    
    print("✨ Exemples de pipelines disponibles !")
    print("Décommentez les lignes ci-dessus pour les tester.")

