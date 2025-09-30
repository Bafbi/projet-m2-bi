// main.tf

# This block tells Terraform which "provider" we need.
# A provider is like a plugin that knows how to talk to an API
# (in this case, the local file system).
terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "2.4.0"
    }
  }
}

# This is a "resource" block. It defines a piece of infrastructure.
# "local_file" is the resource type.
# "hello" is the local name we give it inside our code.
resource "local_file" "hello" {
  content  = "Hello, World! I was created by Terraform."
  filename = "${path.module}/hello.txt"
}