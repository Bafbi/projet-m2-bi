"""
CLI entry point for dbt profile setup.

Usage:
    uv run python -m infrastructure.setup_profiles [options]
"""
import argparse
import sys

from .config import setup_local_logging, logger
from .flows import (
    generate_local_profiles_pipeline,
    setup_dbt_blocks_pipeline,
    setup_dbt_complete_pipeline,
)


def main() -> int:
    """Main CLI entry point."""
    setup_local_logging()
    
    parser = argparse.ArgumentParser(
        description="Configure dbt localement et/ou dans Prefect",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Configuration complète (local + Prefect)
  uv run python -m infrastructure.setup_profiles
  
  # Génération locale uniquement
  uv run python -m infrastructure.setup_profiles --local-only
  
  # Blocs Prefect uniquement (profils déjà générés)
  uv run python -m infrastructure.setup_profiles --blocks-only
  
  # Configuration avec projet GCP personnalisé
  uv run python -m infrastructure.setup_profiles --gcp-project mon-projet
        """
    )
    
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Génère uniquement les profils locaux (pas de blocs Prefect)"
    )
    parser.add_argument(
        "--blocks-only",
        action="store_true",
        help="Configure uniquement les blocs Prefect (skip profils locaux)"
    )
    parser.add_argument(
        "--gcp-project",
        type=str,
        default="test-terraform-473818",
        help="ID du projet GCP (default: test-terraform-473818)"
    )
    parser.add_argument(
        "--credentials-block",
        type=str,
        default="gcp-credentials",
        help="Nom du bloc credentials (default: gcp-credentials)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.local_only:
            # Génération locale uniquement
            logger.info("Mode: Génération locale uniquement")
            generate_local_profiles_pipeline()
        elif args.blocks_only:
            # Blocs Prefect uniquement
            logger.info("Mode: Configuration blocs Prefect uniquement")
            setup_dbt_blocks_pipeline(
                gcp_project=args.gcp_project,
                credentials_block_name=args.credentials_block,
                dbt_commands=["dbt debug"]
            )
        else:
            # Configuration complète
            logger.info("Mode: Configuration complète (local + Prefect)")
            setup_dbt_complete_pipeline(
                gcp_project=args.gcp_project,
                credentials_block_name=args.credentials_block,
                dbt_commands=["dbt debug"]
            )
        
        logger.info("✅ Opération terminée avec succès")
        return 0
    except Exception as exc:
        logger.error(f"❌ Erreur: {exc}", exc_info=True)
        print(f"\n❌ Erreur: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
