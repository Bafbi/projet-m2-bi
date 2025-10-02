# Projet M2 BI

This is a project for M2 BI, featuring infrastructure as code using Terraform/OpenTofu for GCP resources and dbt for data transformation.

## Prerequisites

- [OpenTofu](https://opentofu.org/) or [Terraform](https://www.terraform.io/) installed
- Google Cloud SDK (`gcloud`) installed and authenticated
- A GCP project with billing enabled
- Permissions to create resources in GCP (BigQuery, Storage, Compute Engine, IAM)

## Deployment Procedure

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd projet-m2-bi
   ```

2. **Set up GCP credentials:**
   - Authenticate with GCP:
     ```bash
     gcloud auth login
     gcloud config set project <your-project-id>
     ```
   - Ensure your account has the necessary permissions or use a service account.

3. **Configure variables:**
   - Copy the example variables file and edit it:
     ```bash
     cp infrastructure/terraform.tfvars.example infrastructure/terraform.tfvars
     ```
   - Edit `infrastructure/terraform.tfvars` to set your project ID, state bucket name, dataset IDs, and service account settings.

4. **Deploy the infrastructure:**
   ```bash
   cd infrastructure
   tofu init -backend-config="bucket=<your-state-bucket>"
   tofu plan
   tofu apply
   ```
   Replace `<your-state-bucket>` with the same value configured in `terraform.tfvars`. The backend block already sets the prefix to `terraform/state`.
   Confirm the apply to create:
   - GCS bucket for Terraform state (first run may require a local backend if the bucket does not yet exist)
   - BigQuery datasets (dev and prod)
   - Service account with necessary IAM roles

5. **Export Terraform outputs and generate the dbt profile:**
   ```bash
   tofu output -json > terraform-outputs.json
   cd ..
   python scripts/generate_profiles.py
   ```
   Replace `tofu` with `terraform` if you prefer. The script renders `dbt/profiles.tpl` using the exported JSON and writes `dbt/profiles.yml`. Use `--dry-run` to preview the rendered content or `--outputs-json` to point at a custom file.

6. **Create and place the service account key (if using service account auth):**
   - After apply, note the service account email from the output.
   - Create a key:
     ```bash
     gcloud iam service-accounts keys create .secrets/sa_key.json --iam-account <sa-email>
     ```
   - The generated `dbt/profiles.yml` is already configured to use this key path.

## Usage

- **dbt:** Use the generated `dbt/profiles.yml` for development and production environments.
- **BigQuery:** Access the dev and prod datasets as specified in the Terraform outputs.

## Notes

- The infrastructure uses GCS as the backend for Terraform state. Supply the bucket via `tofu init -backend-config="bucket=..."` (or the Terraform equivalent).
- Service account keys are not committed to version control (ignored in .gitignore).
- For production deployments, consider using CI/CD pipelines with secure credential management.