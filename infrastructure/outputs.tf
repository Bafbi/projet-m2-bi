output "bq_dev_dataset_id" {
  description = "BigQuery dev dataset ID"
  value       = google_bigquery_dataset.dev_dataset.dataset_id
}

output "bq_prod_dataset_id" {
  description = "BigQuery prod dataset ID"
  value       = google_bigquery_dataset.prod_dataset.dataset_id
}

output "sa_email" {
  description = "Service account email created for dbt"
  value       = google_service_account.dbt_sa.email
}

output "project_id" {
  description = "GCP project id"
  value       = var.project_id
}

output "region" {
  description = "GCP region"
  value       = var.region
}

output "sa_key_path" {
  description = "Relative path to the service account key file expected by dbt"
  value       = var.sa_key_path
}