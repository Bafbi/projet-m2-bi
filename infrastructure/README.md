# Infrastructure Deployment Guide

This document explains how to provision the Google Cloud resources and supporting assets used by the Projet M2 BI platform. Follow these steps after cloning the repository and authenticating with Google Cloud.

## Prerequisites

- [OpenTofu](https://opentofu.org/) or [Terraform](https://www.terraform.io/) installed
- Google Cloud SDK (`gcloud`) installed and authenticated
- A GCP project with billing enabled
- Permissions to create resources in BigQuery, Cloud Storage, and IAM

## Deployment Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd projet-m2-bi
   ```

2. **Configure variables**
   ```bash
   cp infrastructure/terraform.tfvars.example infrastructure/terraform.tfvars
   ```
   Edit `infrastructure/terraform.tfvars` to set your project ID, state bucket name, dataset IDs, and service account settings.

3. **Initialize and apply the infrastructure**
   ```bash
   cd infrastructure
   tofu init -backend-config="bucket=<your-state-bucket>"
   tofu plan
   tofu apply
   ```
   Replace `<your-state-bucket>` with the value configured in `terraform.tfvars`. The backend block already fixes the prefix to `terraform/state`.

4. **Export Terraform outputs**
   ```bash
   tofu output -json > terraform-outputs.json
   ```
   Keep this JSON file alongside the Terraform configuration (default path consumed by the profile generator).

5. **Generate the dbt profile**
   ```bash
   cd ..
   python scripts/generate_profiles.py
   ```
   The script reads `infrastructure/terraform-outputs.json`, renders `dbt/profiles.tpl`, and writes `dbt/profiles.yml`. Use `--dry-run` to preview or `--outputs-json` to point at a custom file.

6. **Create and store the service account key (if required)**
   ```bash
   gcloud iam service-accounts keys create .secrets/sa_key.json --iam-account <sa-email>
   ```
   `<sa-email>` is available in the Terraform outputs. The generated `dbt/profiles.yml` is configured to use `.secrets/sa_key.json` by default.

## Notes

- The Terraform remote state uses a GCS bucket; ensure the bucket exists or bootstrap it locally before switching to the remote backend.
- Service account keys must remain outside version control (the `.secrets` directory is ignored by `.gitignore`).
- For production-grade deployments, automate these steps via CI/CD pipelines and secret managers.
