terraform {
  backend "gcs" {
    bucket = var.state_bucket
    prefix = "terraform/state"
  }
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
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

module "infrastructure" {
  source = "./infrastructure"

  project_id       = var.project_id
  region           = var.region
  state_bucket     = var.state_bucket
  bq_dev_dataset_id  = var.bq_dev_dataset_id
  bq_prod_dataset_id = var.bq_prod_dataset_id
  sa_account_id    = var.sa_account_id
  sa_key_path      = var.sa_key_path
}
