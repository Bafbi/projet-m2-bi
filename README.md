# Projet M2 BI

This is a project for M2 BI, featuring infrastructure as code using Terraform/OpenTofu for GCP resources and dbt for data transformation.

## Infrastructure deployment

Detailed prerequisites and step-by-step deployment instructions now live in [`infrastructure/README.md`](infrastructure/README.md).

## Usage

- **dbt:** Use the generated `dbt/profiles.yml` for development and production environments.
- **BigQuery:** Access the dev and prod datasets as specified in the Terraform outputs.

## Notes

- Service account keys are not committed to version control (ignored in `.gitignore`).
- For production deployments, consider using CI/CD pipelines with secure credential management.