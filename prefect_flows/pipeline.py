"""
Flow Prefect pour orchestrer les transformations dbt

Ce module définit les tâches et flows pour exécuter dbt via Prefect.
Il utilise le fichier profiles.yml local (dbt/profiles.yml) généré par 
infrastructure/setup_profiles/flows.py.

Pour générer profiles.yml :
    uv run python -m infrastructure.setup_profiles --local-only
"""
from prefect import flow, task, get_run_logger
from prefect_dbt.cli.commands import DbtCoreOperation
from pathlib import Path


@task(name="dbt-run", retries=2, retry_delay_seconds=30)
def run_dbt_models(target: str = "dev"):
    """
    Exécute les transformations dbt (dbt run)
    
    Cette tâche construit tous les modèles définis dans le projet dbt.
    Les retries permettent de gérer les erreurs temporaires de connexion.
    
    IMPORTANT: Cette tâche utilise le profiles.yml local (dbt/profiles.yml).
    Assurez-vous de le générer avec: uv run python -m infrastructure.setup_profiles --local-only
    
    Args:
        target: Environnement cible (dev ou prod). Correspond au target dans profiles.yml
    
    Returns:
        Résultat de l'exécution dbt
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profiles_dir = project_dir
    
    logger.info(f"🚀 Exécution de dbt run sur l'environnement: {target}")
    logger.info(f"📁 Répertoire du projet: {project_dir}")
    logger.info(f"📋 Fichier de profils: {profiles_dir / 'profiles.yml'}")
    
    # Vérifie que profiles.yml existe
    if not (profiles_dir / "profiles.yml").exists():
        logger.error("❌ Le fichier profiles.yml n'existe pas!")
        logger.error("Générez-le avec: uv run python -m infrastructure.setup_profiles --local-only")
        raise FileNotFoundError(
            f"Le fichier {profiles_dir / 'profiles.yml'} n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles --local-only"
        )

    # Exécute dbt run en utilisant le profiles.yml local
    result = DbtCoreOperation(
        commands=[f"dbt run --target {target}"],
        project_dir=str(project_dir),
        profiles_dir=str(profiles_dir),
        overwrite_profiles=False,
    ).run()
    
    logger.info(f"✅ dbt run terminé avec succès sur {target}")
    return result


@task(name="dbt-test", retries=1)
def test_dbt_models(target: str = "dev"):
    """
    Teste les modèles dbt (dbt test)
    
    Vérifie que les contraintes de qualité des données sont respectées
    (unicité, non-nullité, relations, etc.)
    
    IMPORTANT: Cette tâche utilise le profiles.yml local (dbt/profiles.yml).
    
    Args:
        target: Environnement cible (dev ou prod). Correspond au target dans profiles.yml
    
    Returns:
        Résultat des tests dbt
    """
    logger = get_run_logger()
    project_dir = Path(__file__).parent.parent / "dbt"
    profiles_dir = project_dir
    
    logger.info(f"🧪 Exécution de dbt test sur l'environnement: {target}")
    logger.info(f"📁 Répertoire du projet: {project_dir}")
    
    # Vérifie que profiles.yml existe
    if not (profiles_dir / "profiles.yml").exists():
        logger.error("❌ Le fichier profiles.yml n'existe pas!")
        raise FileNotFoundError(
            f"Le fichier {profiles_dir / 'profiles.yml'} n'existe pas. "
            f"Exécutez: uv run python -m infrastructure.setup_profiles --local-only"
        )
    
    # Exécute dbt test en utilisant le profiles.yml local
    result = DbtCoreOperation(
        commands=[f"dbt test --target {target}"],
        project_dir=str(project_dir),
        profiles_dir=str(profiles_dir),
        overwrite_profiles=False,
    ).run()
    
    logger.info(f"✅ dbt test terminé avec succès sur {target}")
    return result


@flow(name="pipeline-dbt-complet", log_prints=True)
def dbt_full_pipeline(target: str = "dev"):
    """
    Pipeline complète dbt : run + test
    
    Cette pipeline orchestre l'exécution complète de dbt en utilisant les blocs
    Prefect configurés par infrastructure/setup_profiles/flows.py.
    
    Args:
        target: Environnement cible (dev ou prod). Par défaut "dev".
                - dev : utilise le bloc 'dbt-cli-profile-dev' (dataset dev, 1 thread)
                - prod : utilise le bloc 'dbt-cli-profile-prod' (dataset prod, 4 threads)
    
    Returns:
        Dict contenant les résultats de run et test
    
    Exemples d'utilisation:
        
        En local (environnement dev):
            python prefect_flows/pipeline.py
            
        En local (environnement prod):
            python prefect_flows/pipeline.py --target prod
        
        Avec Prefect Cloud:
            prefect deployment build prefect_flows/pipeline.py:dbt_full_pipeline -n "dbt-dev" -p default-pool
            prefect deployment apply dbt_full_pipeline-deployment.yaml
            prefect deployment run pipeline-dbt-complet/dbt-dev --param target=dev
    """
    logger = get_run_logger()
    
    logger.info(f"🚀 Démarrage de la pipeline dbt complète (environnement: {target})...")
    
    # 1. Exécute les transformations dbt
    logger.info("📊 Étape 1/2 : Exécution des modèles dbt (dbt run)...")
    run_result = run_dbt_models(target=target)
    logger.info(f"✅ Modèles dbt exécutés avec succès sur l'environnement {target}")
    
    # 2. Teste les modèles (seulement si run a réussi)
    logger.info("🧪 Étape 2/2 : Test des modèles dbt (dbt test)...")
    test_result = test_dbt_models(target=target)
    logger.info(f"✅ Tests dbt passés avec succès sur l'environnement {target}")
    
    logger.info(f"🎉 Pipeline terminée avec succès sur l'environnement {target}!")
    
    return {
        "target": target,
        "run": run_result,
        "test": test_result,
    }


if __name__ == "__main__":
    """
    Point d'entrée pour l'exécution locale.
    
    Usage:
        # Environnement dev (par défaut)
        uv run python prefect_flows/pipeline.py
        
        # Pour prod, modifiez l'appel ci-dessous ou utilisez Prefect CLI
    """
    # Exécution locale pour tester (environnement dev par défaut)
    dbt_full_pipeline(target="dev")

