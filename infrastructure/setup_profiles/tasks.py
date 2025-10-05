"""
Prefect tasks for dbt profile generation and block configuration.
"""
from pathlib import Path
import json
import yaml
from string import Template
from typing import Any, Dict

from prefect import task, get_run_logger
from prefect_gcp.credentials import GcpCredentials
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile, DbtCoreOperation

from .config import logger, ProfileGenerationError


@task(name="parse-template-targets")
def parse_template_targets(template_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Parse le template dbt pour extraire les targets définis
    
    Args:
        template_path: Chemin vers le template profiles.tpl.yml
    
    Returns:
        Dict avec les noms des targets et leurs configurations
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Parsing du template {template_path} pour extraire les targets...")
    
    if not template_path.exists():
        raise ProfileGenerationError(f"Template introuvable: {template_path}")
    
    template_text = template_path.read_text(encoding="utf-8")
    
    # Parse le YAML pour extraire la structure (sans substitution des variables)
    try:
        # On parse le template brut pour voir la structure
        template_data = yaml.safe_load(template_text)
    except yaml.YAMLError as exc:
        raise ProfileGenerationError(
            f"Erreur lors du parsing YAML du template: {exc}"
        ) from exc
    
    # Extraire le profile_name et les outputs
    if not template_data or not isinstance(template_data, dict):
        raise ProfileGenerationError("Le template doit contenir un dictionnaire de profils")
    
    # Le template devrait avoir une seule clé de profil (ex: "projet_m2_bi")
    profile_name = list(template_data.keys())[0]
    profile_config = template_data[profile_name]
    
    if "outputs" not in profile_config:
        raise ProfileGenerationError(f"Le profil '{profile_name}' n'a pas de section 'outputs'")
    
    targets = profile_config["outputs"]
    run_logger.info(f"Targets trouvés dans le template: {list(targets.keys())}")
    
    return {
        "profile_name": profile_name,
        "default_target": profile_config.get("target", list(targets.keys())[0]),
        "targets": targets
    }


@task(name="load-terraform-outputs")
def load_terraform_outputs(outputs_path: Path) -> Dict[str, Any]:
    """
    Charge les outputs Terraform depuis un fichier JSON
    
    Args:
        outputs_path: Chemin vers le fichier terraform-outputs.json
    
    Returns:
        Dict contenant les outputs Terraform
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Chargement des outputs Terraform depuis {outputs_path}")
    
    if not outputs_path.exists():
        raise ProfileGenerationError(
            f"Fichier d'outputs Terraform introuvable: {outputs_path}\n"
            "Exécutez d'abord: tofu output -json > terraform-outputs.json"
        )
    
    try:
        text = outputs_path.read_text(encoding="utf-8")
        payload = json.loads(text)
        run_logger.info(f"Outputs chargés avec succès: {sorted(payload.keys())}")
        return payload
    except json.JSONDecodeError as exc:
        raise ProfileGenerationError(
            f"Erreur lors du parsing JSON de {outputs_path}: {exc}"
        ) from exc


@task(name="build-profile-context")
def build_profile_context(
    outputs: Dict[str, Any],
    project_root: Path,
    output_path: Path
) -> Dict[str, str]:
    """
    Construit le contexte pour le rendu du template de profil dbt
    
    Args:
        outputs: Outputs Terraform
        project_root: Racine du projet
        output_path: Chemin du fichier de sortie (pour les chemins relatifs)
    
    Returns:
        Dict contenant les variables pour le template
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    required_keys = [
        "project_id",
        "region",
        "bq_dev_dataset_id",
        "bq_prod_dataset_id",
        "sa_key_path",
    ]
    missing = [key for key in required_keys if key not in outputs]
    if missing:
        raise ProfileGenerationError(
            f"Outputs Terraform manquants: {', '.join(missing)}"
        )
    
    def unwrap(key: str) -> Any:
        """Unwrap Terraform output value."""
        value = outputs[key]
        if isinstance(value, dict) and "value" in value:
            return value["value"]
        return value
    
    raw_sa_path = unwrap("sa_key_path")
    sa_path = Path(raw_sa_path)
    if not sa_path.is_absolute():
        sa_path = project_root / sa_path
    
    # Assurer que le répertoire existe
    sa_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculer le chemin relatif
    try:
        relative_sa_path = sa_path.relative_to(output_path.parent)
    except ValueError:
        relative_sa_path = sa_path
    
    context = {
        "project": unwrap("project_id"),
        "region": unwrap("region"),
        "dev_dataset": unwrap("bq_dev_dataset_id"),
        "prod_dataset": unwrap("bq_prod_dataset_id"),
        "sa_key_path": relative_sa_path.as_posix(),
    }
    
    run_logger.info(f"Contexte construit: project={context['project']}, region={context['region']}")
    return context


@task(name="render-profile-template")
def render_profile_template(template_path: Path, context: Dict[str, str]) -> str:
    """
    Rend le template de profil dbt avec le contexte fourni
    
    Args:
        template_path: Chemin vers le template profiles.tpl.yml
        context: Variables pour le rendu du template
    
    Returns:
        Contenu du profil rendu
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Rendu du template {template_path}")
    
    if not template_path.exists():
        raise ProfileGenerationError(f"Template introuvable: {template_path}")
    
    template_text = template_path.read_text(encoding="utf-8")
    try:
        rendered = Template(template_text).substitute(context)
        run_logger.info("Template rendu avec succès")
        return rendered
    except KeyError as exc:
        missing = exc.args[0]
        raise ProfileGenerationError(
            f"Le template attend une clé manquante: '{missing}'"
        ) from exc


@task(name="write-local-profile")
def write_local_profile(content: str, output_path: Path) -> Path:
    """
    Écrit le profil dbt dans un fichier local
    
    Args:
        content: Contenu du profil à écrire
        output_path: Chemin de destination
    
    Returns:
        Path du fichier créé
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    run_logger.info(f"Profil écrit dans {output_path}")
    return output_path


@task(name="setup-gcp-credentials")
def setup_gcp_credentials(credentials_block_name: str, gcp_project: str, service_account_file: Path):
    """
    Crée et sauvegarde les credentials GCP depuis un fichier de service account
    
    Args:
        credentials_block_name: Nom du bloc où sauvegarder les credentials GCP
        gcp_project: ID du projet GCP
        service_account_file: Chemin vers le fichier JSON du service account
    
    Returns:
        GcpCredentials: Les credentials GCP créées
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Chargement des credentials GCP depuis le fichier '{service_account_file}'...")
    
    if not service_account_file.exists():
        raise FileNotFoundError(f"Le fichier de service account n'existe pas: {service_account_file}")
    
    credentials = GcpCredentials(
        project=gcp_project,
        service_account_info=service_account_file.read_text(encoding="utf-8")
    )
    credentials.save(credentials_block_name, overwrite=True)
    run_logger.info(f"Credentials GCP créées et sauvegardées dans le bloc '{credentials_block_name}'")
    return credentials


@task(name="setup-bigquery-target")
def setup_bigquery_target(
    credentials: GcpCredentials,
    schema_name: str,
    target_configs_block_name: str,
    threads: int = 1,
    location: str = "europe-west9"
):
    """
    Configure et sauvegarde les configurations BigQuery pour dbt
    
    Args:
        credentials: Credentials GCP
        schema_name: Nom du schéma BigQuery (dataset)
        target_configs_block_name: Nom du bloc où sauvegarder la configuration
        threads: Nombre de threads pour dbt (default: 1)
        location: Région BigQuery (default: europe-west9)
    
    Returns:
        BigQueryTargetConfigs: La configuration BigQuery
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Configuration de BigQuery avec le schéma '{schema_name}' (threads={threads}, location={location})...")
    target_configs = BigQueryTargetConfigs(
        schema=schema_name,  # also known as dataset
        credentials=credentials,
        project=credentials.project,
        threads=threads,
        extras={"location": location},
    )
    target_configs.save(target_configs_block_name, overwrite=True)
    run_logger.info(f"Configuration BigQuery sauvegardée dans le bloc '{target_configs_block_name}'")
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
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Configuration du profil dbt '{profile_name}' avec target '{target_name}'...")
    dbt_cli_profile = DbtCliProfile(
        name=profile_name,
        target=target_name,
        target_configs=target_configs,
    )
    dbt_cli_profile.save(dbt_profile_block_name, overwrite=True)
    run_logger.info(f"Profil dbt sauvegardé dans le bloc '{dbt_profile_block_name}'")
    return dbt_cli_profile


@task(name="setup-dbt-operation")
def setup_dbt_operation(
    dbt_profile: DbtCliProfile | None,
    dbt_profile_block_name: str | None,
    dbt_commands: list[str],
    dbt_operation_block_name: str,
    project_dir: Path
):
    """
    Configure et sauvegarde l'opération dbt
    
    Args:
        dbt_profile: Profil dbt (optionnel si dbt_profile_block_name est fourni)
        dbt_profile_block_name: Nom du bloc contenant le profil dbt (optionnel si dbt_profile est fourni)
        dbt_commands: Liste des commandes dbt à exécuter
        dbt_operation_block_name: Nom du bloc où sauvegarder l'opération
        project_dir: Répertoire du projet dbt
    
    Returns:
        DbtCoreOperation: L'opération dbt configurée
    """
    try:
        run_logger = get_run_logger()
    except Exception:
        run_logger = logger
    
    run_logger.info(f"Configuration de l'opération dbt avec les commandes: {dbt_commands}...")
    dbt_cli_profile = dbt_profile or DbtCliProfile.load(dbt_profile_block_name)
    
    dbt_core_operation = DbtCoreOperation(
        project_dir=project_dir,
        commands=dbt_commands,
        dbt_cli_profile=dbt_cli_profile,
        overwrite_profiles=True,
    )
    dbt_core_operation.save(dbt_operation_block_name, overwrite=True)
    run_logger.info(f"Opération dbt sauvegardée dans le bloc '{dbt_operation_block_name}'")
    return dbt_core_operation
