"""
Flow Prefect pour orchestrer les transformations dbt
"""
from prefect import flow, task
from prefect_dbt.cli.commands import DbtCoreOperation
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile
from prefect_gcp.credentials import GcpCredentials
from pathlib import Path
from dotenv import load_dotenv
import os


# Chargement automatique du .env en local (si présent)
try:
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv non installé, pas grave (variables env système utilisées)
    print("python-dotenv non installé, variables env système utilisées")
    pass
    

def _build_dbt_cli_profile_from_gcp_block() -> DbtCliProfile:
    """
    Construit un profil dbt BigQuery à partir d'un Block Prefect GCP Credentials.
    
    Le Block GCP doit être créé au préalable dans Prefect (local ou cloud).
    Cette approche élimine le besoin de fichiers de clés locaux et centralise
    la gestion des credentials.

    Variables d'environnement requises:
      - PREFECT_GCP_CREDENTIALS_BLOCK: nom du block GcpCredentials (ex: "sa-key")
      - DBT_TARGET: cible dbt ("dev" ou "prod")
      - DBT_BIGQUERY_DATASET_DEV: dataset BigQuery pour dev (schema)
      - DBT_BIGQUERY_DATASET_PROD: dataset BigQuery pour prod (schema)
      - DBT_PROFILE_NAME: nom du profil (par défaut "projet_m2_bi")
      
    Convention:
      - Local: DBT_TARGET=dev (par défaut)
      - Prefect Cloud: DBT_TARGET=prod (à configurer manuellement)
      
    Raises:
        ValueError: Si le Block GCP n'existe pas ou si les variables env sont manquantes
    """

    block_name = os.getenv("PREFECT_GCP_CREDENTIALS_BLOCK", "sa-key")
    target = os.getenv("DBT_TARGET", "dev")
    dataset_dev = os.getenv("DBT_BIGQUERY_DATASET_DEV", "test_terraform_473818_dev")
    dataset_prod = os.getenv("DBT_BIGQUERY_DATASET_PROD", "test_terraform_473818_prod")
    dataset = dataset_dev if target == "dev" else dataset_prod
    profile_name = os.getenv("DBT_PROFILE_NAME", "projet_m2_bi")

    credentials = GcpCredentials.load(block_name)
    target_configs = BigQueryTargetConfigs(
        schema=dataset,
        credentials=credentials,
    )

    return DbtCliProfile(
        name=profile_name,
        target=target,
        target_configs=target_configs,
    )


@task(name="dbt-run", retries=2, retry_delay_seconds=30)
def run_dbt_models():
    """
    Exécute les transformations dbt (dbt run)
    
    Cette tâche construit tous les modèles définis dans le projet dbt
    en utilisant le Block GCP Credentials Prefect pour l'authentification.
    Les retries permettent de gérer les erreurs temporaires de connexion.
    """
    project_dir = Path(__file__).parent.parent / "dbt"
    
    # Construction du profil dbt depuis le Block GCP
    dbt_cli_profile = _build_dbt_cli_profile_from_gcp_block()
    
    result = DbtCoreOperation(
        commands=["dbt run"],
        project_dir=str(project_dir),
        dbt_cli_profile=dbt_cli_profile,
        overwrite_profiles=True,
    ).run()
    
    return result


@task(name="dbt-test", retries=1)
def test_dbt_models():
    """
    Teste les modèles dbt (dbt test)
    
    Vérifie que les contraintes de qualité des données sont respectées
    (unicité, non-nullité, relations, etc.)
    """
    project_dir = Path(__file__).parent.parent / "dbt"
    
    # Construction du profil dbt depuis le Block GCP
    dbt_cli_profile = _build_dbt_cli_profile_from_gcp_block()
    
    result = DbtCoreOperation(
        commands=["dbt test"],
        project_dir=str(project_dir),
        dbt_cli_profile=dbt_cli_profile,
        overwrite_profiles=True,
    ).run()
    
    return result


@flow(name="pipeline-dbt-complet", log_prints=True)
def dbt_full_pipeline():
    """
    Pipeline complète
    
    En local :
        python prefect/pipeline.py
        
    Prefect Cloud :
        prefect-cloud deploy prefect/pipeline.py:dbt_full_pipeline
    """
    print("Démarrage de la pipeline...")
    
    # 1. Exécute les transformations
    print("Étape 1/3 : Exécution des modèles dbt...")
    run_result = run_dbt_models()
    print(f"Modèles dbt exécutés avec succès")
    
    # 2. Teste les modèles (seulement si run a réussi)
    print("Étape 2/3 : Test des modèles dbt...")
    test_result = test_dbt_models()
    print(f"Tests dbt passés avec succès")

    
    print("Pipeline terminée avec succès !")
    
    return {
        "run": run_result,
        "test": test_result,
    }

if __name__ == "__main__":
    # Exécution locale pour tester
    dbt_full_pipeline()

