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
     cp terraform.tfvars.example terraform.tfvars
     ```
   - Edit `terraform.tfvars` to set your project ID and other variables:

4. **Initialize Terraform/OpenTofu:**
   ```bash
   tofu init
   ```
   This will download providers and set up the GCS backend for state storage.

5. **Plan the deployment:**
   ```bash
   tofu plan
   ```
   Review the plan to ensure it creates the expected resources.

6. **Apply the infrastructure:**
   ```bash
   tofu apply
   ```
   Confirm the apply to create:
   - GCS bucket for Terraform state
   - BigQuery datasets (dev and prod)
   - Service account with necessary IAM roles
   - dbt profiles.yml file

7. **Create and place the service account key (if using service account auth):**
   - After apply, note the service account email from the output.
   - Create a key:
     ```bash
     gcloud iam service-accounts keys create .secrets/sa_key.json --iam-account <sa-email>
     ```
   - The `dbt/profiles.yml` will be configured to use this key.

## Usage

- **dbt:** Use the generated `dbt/profiles.yml` for development and production environments.
- **BigQuery:** Access the dev and prod datasets as specified in the Terraform outputs.

## Notes

- The infrastructure uses GCS as the backend for Terraform state.
- Service account keys are not committed to version control (ignored in .gitignore).
- For production deployments, consider using CI/CD pipelines with secure credential management.