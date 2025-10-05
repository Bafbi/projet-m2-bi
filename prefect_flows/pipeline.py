"""
Flow Prefect pour orchestrer les transformations dbt
"""
from prefect import flow, task
from prefect_dbt.cli.commands import DbtCoreOperation
from pathlib import Path
from prefect_dbt.cli import DbtCliProfile


@task(name="dbt-run", retries=2, retry_delay_seconds=30)
def run_dbt_models():
    """
    Exécute les transformations dbt (dbt run)
    
    Cette tâche construit tous les modèles définis dans le projet dbt.
    Les retries permettent de gérer les erreurs temporaires de connexion.
    """
    project_dir = Path(__file__).parent.parent / "dbt"
    dbt_cli_profile = DbtCliProfile.load("profile").get_profile()
    print(f"Using dbt profile: {dbt_cli_profile}")

    result = DbtCoreOperation(
        commands=["dbt run"],
        project_dir=str(project_dir),
        overwrite_profiles=True,
        dbt_cli_profile=dbt_cli_profile,
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
    
    result = DbtCoreOperation(
        commands=["dbt test"],
        project_dir=str(project_dir),
        profiles_dir=str(project_dir),
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

