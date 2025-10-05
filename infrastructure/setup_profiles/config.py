"""
Configuration and error classes for dbt setup.
"""
import logging


# Configuration du logging pour l'exécution locale
logger = logging.getLogger("dbt_setup")


def setup_local_logging() -> None:
    """Configure le logging pour l'exécution locale."""
    if logging.getLogger().hasHandlers():
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


class ProfileGenerationError(RuntimeError):
    """Raised when profile generation fails."""
