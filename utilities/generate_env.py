#!/usr/bin/env python3
"""
Script pour générer le fichier .env à partir des outputs Terraform.

Ce script lit infrastructure/terraform-outputs.json (généré par `tofu output -json`)
et crée automatiquement un fichier .env avec les variables d'environnement
nécessaires pour Prefect.

Usage:
    python utilities/generate_env.py
    python utilities/generate_env.py --dry-run
    python utilities/generate_env.py --outputs-json custom-path.json
"""

import argparse
import json
import sys
from pathlib import Path


def load_terraform_outputs(outputs_path: Path) -> dict:
    """
    Charge les outputs Terraform depuis un fichier JSON.
    
    Args:
        outputs_path: Chemin vers le fichier terraform-outputs.json
        
    Returns:
        Dictionnaire des outputs Terraform
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        json.JSONDecodeError: Si le JSON est invalide
    """
    if not outputs_path.exists():
        raise FileNotFoundError(
            f"Le fichier {outputs_path} n'existe pas.\n"
            "Exécutez d'abord : cd infrastructure && tofu output -json > terraform-outputs.json"
        )
    
    with open(outputs_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_env_content(tf_outputs: dict, block_name: str = "sa-key") -> str:
    """
    Génère le contenu du fichier .env à partir des outputs Terraform.
    
    Args:
        tf_outputs: Dictionnaire des outputs Terraform
        block_name: Nom du block Prefect GCP Credentials (défaut: "sa-key")
        
    Returns:
        Contenu du fichier .env sous forme de string
    """
    # Extraction des valeurs depuis la structure Terraform outputs
    dev_dataset = tf_outputs.get("bq_dev_dataset_id", {}).get("value", "")
    prod_dataset = tf_outputs.get("bq_prod_dataset_id", {}).get("value", "")
    project_id = tf_outputs.get("project_id", {}).get("value", "")
    region = tf_outputs.get("region", {}).get("value", "")
    
    # Template du fichier .env
    env_template = f"""# Configuration Prefect - Générée automatiquement depuis Terraform
    # NE PAS COMMITTER CE FICHIER - Ajouté dans .gitignore

    # === Configuration GCP Block ===
    # Nom du Block Prefect GCP Credentials créé dans Prefect Cloud/Server
    PREFECT_GCP_CREDENTIALS_BLOCK={block_name}

    # === Configuration dbt ===
    # Cible dbt : "dev" ou "prod"
    DBT_TARGET=dev

    # Datasets BigQuery (générés depuis Terraform)
    DBT_BIGQUERY_DATASET_DEV={dev_dataset}
    DBT_BIGQUERY_DATASET_PROD={prod_dataset}

    # Nom du profil dbt (doit correspondre à dbt_project.yml)
    DBT_PROFILE_NAME=projet_m2_bi

    # === Informations GCP (référence) ===
    # Ces variables ne sont pas utilisées par le flow mais documentent l'environnement
    GCP_PROJECT_ID={project_id}
    GCP_REGION={region}
    """
    return env_template.strip() + "\n"


def write_env_file(env_path: Path, content: str, dry_run: bool = False):
    """
    Écrit le fichier .env ou affiche son contenu en mode dry-run.
    
    Args:
        env_path: Chemin du fichier .env à créer
        content: Contenu à écrire
        dry_run: Si True, affiche seulement le contenu sans écrire
    """
    if dry_run:
        print("=== Mode dry-run : Contenu du .env à générer ===\n")
        print(content)
        print(f"\n=== Fichier non écrit (dry-run). Chemin cible : {env_path} ===")
        return
    
    # Création du fichier .env
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Fichier .env généré avec succès : {env_path}")
    print("\nVariables configurées :")
    for line in content.split("\n"):
        if line and not line.startswith("#") and "=" in line:
            var_name = line.split("=")[0]
            print(f"  - {var_name}")


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description="Génère le fichier .env depuis les outputs Terraform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Exemples:
        python utilities/generate_env.py
        python utilities/generate_env.py --dry-run
        python utilities/generate_env.py --outputs-json infrastructure/custom-outputs.json
        python utilities/generate_env.py --block-name my-gcp-credentials
        """
    )
    
    parser.add_argument(
        "--outputs-json",
        type=Path,
        default=Path("infrastructure/terraform-outputs.json"),
        help="Chemin vers le fichier terraform-outputs.json (défaut: infrastructure/terraform-outputs.json)"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".env"),
        help="Chemin du fichier .env à générer (défaut: .env à la racine du projet)"
    )
    
    parser.add_argument(
        "--block-name",
        type=str,
        default="sa-key",
        help="Nom du Block Prefect GCP Credentials (défaut: sa-key)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche le contenu généré sans écrire le fichier"
    )
    
    args = parser.parse_args()
    
    try:
        # Chargement des outputs Terraform
        print(f"📖 Lecture des outputs Terraform : {args.outputs_json}")
        tf_outputs = load_terraform_outputs(args.outputs_json)
        
        # Génération du contenu .env
        env_content = generate_env_content(tf_outputs, args.block_name)
        
        # Écriture du fichier .env
        write_env_file(args.output, env_content, args.dry_run)
        
    except FileNotFoundError as e:
        print(f"❌ Erreur : {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON : {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

