variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west9"
}

variable "state_bucket" {
  description = "GCS bucket for Terraform state"
  type        = string
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "bi_dataset"
}