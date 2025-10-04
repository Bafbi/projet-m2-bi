"""
Flow Prefect pour configurer les blocs GCP et dbt
"""
from pathlib import Path
from prefect import flow, task
from prefect.blocks.system import Secret
from prefect_gcp.credentials import GcpCredentials
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile, DbtCoreOperation


@task(name="setup-gcp-credentials")
def setup_gcp_credentials(credentials_block_name: str, gcp_project: str, service_account_file: Path):
    """
    Crée et sauvegarde les credentials GCP depuis un fichier de service account
    
    Args:
        credentials_block_name: Nom du bloc où sauvegarder les credentials GCP
        service_account_file: Chemin vers le fichier JSON du service account
    
    Returns:
        GcpCredentials: Les credentials GCP créées
    """
    print(f"Chargement des credentials GCP depuis le fichier '{service_account_file}'...")
    
    if not service_account_file.exists():
        raise FileNotFoundError(f"Le fichier de service account n'existe pas: {service_account_file}")
    
    credentials = GcpCredentials(
      project=gcp_project,
      service_account_info=service_account_file.read_text(encoding="utf-8")
    )
    credentials.save(credentials_block_name, overwrite=True)
    print(f"Credentials GCP créées et sauvegardées dans le bloc '{credentials_block_name}'")
    return credentials


@task(name="setup-bigquery-target")
def setup_bigquery_target(
    credentials: GcpCredentials,
    schema_name: str,
    target_configs_block_name: str
):
    """
    Configure et sauvegarde les configurations BigQuery pour dbt
    
    Args:
        credentials: Credentials GCP
        schema_name: Nom du schéma BigQuery (dataset)
        target_configs_block_name: Nom du bloc où sauvegarder la configuration
    
    Returns:
        BigQueryTargetConfigs: La configuration BigQuery
    """
    print(f"Configuration de BigQuery avec le schéma '{schema_name}'...")
    target_configs = BigQueryTargetConfigs(
        schema=schema_name,  # also known as dataset
        credentials=credentials,
        project=credentials.project,
        threads=1,
        extras={"location": "europe-west9"},
    )
    # print( target_configs.get_configs())
    target_configs.save(target_configs_block_name, overwrite=True)
    print(f"Configuration BigQuery sauvegardée dans le bloc '{target_configs_block_name}'")
    return target_configs


@task(name="setup-dbt-profile")
def setup_dbt_profile(
    target_configs: BigQueryTargetConfigs,
    profile_name: str,
    target_name: str,
    dbt_profile_block_name: str
):
    """
    Configure et sauvegarde le profil dbt
    
    Args:
        target_configs: Configuration BigQuery
        profile_name: Nom du profil dbt
        target_name: Nom de la target dbt
        dbt_profile_block_name: Nom du bloc où sauvegarder le profil
    
    Returns:
        DbtCliProfile: Le profil dbt configuré
    """
    print(f"Configuration du profil dbt '{profile_name}' avec target '{target_name}'...")
    dbt_cli_profile = DbtCliProfile(
        name=profile_name,
        target=target_name,
        target_configs=target_configs,
    )
    # print(dbt_cli_profile.get_profile())
    dbt_cli_profile.save(dbt_profile_block_name, overwrite=True)
    print(f"Profil dbt sauvegardé dans le bloc '{dbt_profile_block_name}'")
    return dbt_cli_profile


@task(name="setup-dbt-operation")
def setup_dbt_operation(
    dbt_profile: DbtCliProfile | None,
    dbt_profile_block_name: str | None,
    dbt_commands: list[str],
    dbt_operation_block_name: str
):
    """
    Configure et sauvegarde l'opération dbt
    
    Args:
        dbt_profile: Profil dbt (optionnel si dbt_profile_block_name est fourni)
        dbt_profile_block_name: Nom du bloc contenant le profil dbt (optionnel si dbt_profile est fourni)
        dbt_commands: Liste des commandes dbt à exécuter
        dbt_operation_block_name: Nom du bloc où sauvegarder l'opération
    
    Returns:
        DbtCoreOperation: L'opération dbt configurée
    """
    print(f"Configuration de l'opération dbt avec les commandes: {dbt_commands}...")
    dbt_cli_profile = dbt_profile or DbtCliProfile.load(dbt_profile_block_name).get_profile()
    project_dir = Path(__file__).parent.parent / "dbt"
    
    # Check the profile is valid
    # print(f"Using dbt profile: {dbt_cli_profile.get_profile()}")
    
    
    dbt_core_operation = DbtCoreOperation(
        project_dir=project_dir,
        commands=dbt_commands,
        dbt_cli_profile=dbt_cli_profile,
        overwrite_profiles=True,
    )
    dbt_core_operation.save(dbt_operation_block_name, overwrite=True)
    print(f"Opération dbt sauvegardée dans le bloc '{dbt_operation_block_name}'")
    return dbt_core_operation


@flow(name="setup-dbt-blocks", log_prints=True)
def setup_dbt_blocks_pipeline(
    gcp_project: str,
    credentials_block_name: str = "gcp-credentials",
    service_account_file: Path | None = None,
    schema_name: str = "dbt_dataset",
    target_configs_block_name: str = "bigquery-target-configs",
    profile_name: str = "dbt_profile",
    target_name: str = "dev",
    dbt_profile_block_name: str = "dbt-cli-profile",
    dbt_commands: list[str] = None,
    dbt_operation_block_name: str = "dbt-core-operation"
):
    """
    Pipeline complète pour configurer tous les blocs Prefect nécessaires pour dbt
    
    Cette pipeline configure les blocs dans l'ordre suivant:
    1. Crée les credentials GCP depuis un fichier JSON
    2. Configure BigQuery comme target dbt
    3. Configure le profil dbt
    4. Configure l'opération dbt
    
    En local:
        python prefect/block.py
    
    Args:
        credentials_block_name: Nom du bloc où sauvegarder les credentials GCP
        service_account_file: Chemin vers le fichier JSON du service account (default: .secret/sa_key.json)
        schema_name: Nom du dataset BigQuery
        target_configs_block_name: Nom du bloc pour la config BigQuery
        profile_name: Nom du profil dbt
        target_name: Nom de la target dbt (dev, prod, etc.)
        dbt_profile_block_name: Nom du bloc pour le profil dbt
        dbt_commands: Liste des commandes dbt (default: ["dbt run"])
        dbt_operation_block_name: Nom du bloc pour l'opération dbt
    """
    if dbt_commands is None:
        dbt_commands = ["dbt debug"]
    
    if service_account_file is None:
        service_account_file = Path(__file__).parent.parent / ".secrets" / "sa_key.json"

    print("Démarrage de la configuration des blocs dbt...")
    
    # 1. Crée les credentials GCP depuis le fichier
    print("\nÉtape 1/4 : Création des credentials GCP...")
    credentials = setup_gcp_credentials(credentials_block_name, gcp_project, service_account_file)
    
    # 2. Configure BigQuery
    print("\nÉtape 2/4 : Configuration de BigQuery...")
    target_configs = setup_bigquery_target(
        credentials=credentials,
        schema_name=schema_name,
        target_configs_block_name=target_configs_block_name
    )
    
    # 3. Configure le profil dbt
    print("\nÉtape 3/4 : Configuration du profil dbt...")
    dbt_profile = setup_dbt_profile(
        target_configs=target_configs,
        profile_name=profile_name,
        target_name=target_name,
        dbt_profile_block_name=dbt_profile_block_name
    )
    
    # 4. Configure l'opération dbt
    print("\nÉtape 4/4 : Configuration de l'opération dbt...")
    dbt_operation = setup_dbt_operation(
        dbt_profile=dbt_profile,
        dbt_profile_block_name=dbt_profile_block_name,
        dbt_commands=dbt_commands,
        dbt_operation_block_name=dbt_operation_block_name
    )
    
    # 5. Test de l'opération dbt
    print("\nTest de l'opération dbt...")
    result = dbt_operation.run()
    print(f"Résultat de l'opération dbt: {result}")

    print("\n✅ Configuration des blocs dbt terminée avec succès !")
    print(f"Vous pouvez maintenant utiliser le bloc '{dbt_operation_block_name}' dans vos flows")
    
    return {
        "credentials": credentials_block_name,
        "target_configs": target_configs_block_name,
        "dbt_profile": dbt_profile_block_name,
        "dbt_operation": dbt_operation_block_name
    }


if __name__ == "__main__":

    # Exécution locale pour tester
    # Vous pouvez personnaliser les paramètres ici
    setup_dbt_blocks_pipeline(
        gcp_project="test-terraform-473818",
        credentials_block_name="sa-key",
        schema_name="test_terraform_473818_dev",
        profile_name="projet_m2_bi",
        target_name="dev",
        dbt_commands=["dbt debug"]
    )