output "bq_dev_dataset_id" {
  description = "BigQuery development dataset ID"
  value = module.infrastructure.bq_dev_dataset_id
}

output "bq_prod_dataset_id" {
  description = "BigQuery production dataset ID"
  value = module.infrastructure.bq_prod_dataset_id
}

output "sa_email" {
  description = "Service account email"
  value = module.infrastructure.sa_email
}
