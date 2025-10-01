terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.0"
    }
  }
}


# Dev dataset
resource "google_bigquery_dataset" "dev_dataset" {
  dataset_id    = var.bq_dev_dataset_id
  location      = var.region
  description   = "Development dataset for BI project"
  friendly_name = "BI Dataset (dev)"
  default_table_expiration_ms = 7776000000 # 90 days
}

# Prod dataset
resource "google_bigquery_dataset" "prod_dataset" {
  dataset_id    = var.bq_prod_dataset_id
  location      = var.region
  description   = "Production dataset for BI project"
  friendly_name = "BI Dataset (prod)"
}

# Generate dbt profiles.yml from Terraform outputs (written into repository dbt/)
resource "local_file" "dbt_profiles" {
  content  = templatefile("${path.module}/profiles.tpl", {
    project      = var.project_id
    region       = var.region
    dev_dataset  = google_bigquery_dataset.dev_dataset.dataset_id
    prod_dataset = google_bigquery_dataset.prod_dataset.dataset_id
    sa_key_path  = var.sa_key_path
  })
  filename = "${path.root}/dbt/profiles.yml"
}

# Ensure .secrets dir exists (placeholder) so user can drop SA key there; content empty
resource "local_file" "secrets_placeholder" {
  content  = ""
  filename = "${path.root}/${trimspace(replace(var.sa_key_path, "/${basename(var.sa_key_path)}", ""))}/.placeholder"
}

# Service account for dbt and minimal IAM bindings
resource "google_service_account" "dbt_sa" {
  account_id   = var.sa_account_id
  display_name = "DBT service account"
}

# Grant permissions required for dbt workflows (adjust as needed)
resource "google_project_iam_member" "sa_bq_dataeditor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dbt_sa.email}"
}

resource "google_project_iam_member" "sa_bq_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dbt_sa.email}"
}

resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.dbt_sa.email}"
}