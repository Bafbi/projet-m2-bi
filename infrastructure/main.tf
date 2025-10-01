terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

# Uncomment the backend block after creating the bucket
terraform {
  backend "gcs" {
    bucket = var.state_bucket
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "terraform_state" {
  name          = var.state_bucket
  location      = var.region
  force_destroy = true

  versioning {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }
}

# resource "google_bigquery_dataset" "dev_dataset" {
#   dataset_id    = var.bq_dataset_id
#   location      = var.region
#   description   = "Dataset for BI project"
#   friendly_name = "BI Dataset"
# }