"""
Setup profiles package for dbt configuration.

This package provides tools to generate dbt profiles both locally
and as Prefect blocks for orchestration.
"""
from .flows import (
    generate_local_profiles_pipeline,
    setup_dbt_blocks_pipeline,
    setup_dbt_complete_pipeline,
)
from .tasks import (
    parse_template_targets,
    load_terraform_outputs,
    build_profile_context,
    render_profile_template,
    write_local_profile,
    setup_gcp_credentials,
    setup_bigquery_target,
    setup_dbt_profile,
    setup_dbt_operation,
)

__all__ = [
    "generate_local_profiles_pipeline",
    "setup_dbt_blocks_pipeline",
    "setup_dbt_complete_pipeline",
    "parse_template_targets",
    "load_terraform_outputs",
    "build_profile_context",
    "render_profile_template",
    "write_local_profile",
    "setup_gcp_credentials",
    "setup_bigquery_target",
    "setup_dbt_profile",
    "setup_dbt_operation",
]
