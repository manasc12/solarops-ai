# SolarOps AI — Terraform reference (illustrative)
#
# Provisions a container registry placeholder. This is intentionally minimal
# scaffolding to show where infrastructure-as-code lives; extend with your
# cloud provider's compute, networking, and secret resources for production.

terraform {
  required_version = ">= 1.5.0"
}

variable "project" {
  description = "Project / deployment name"
  type        = string
  default     = "solarops-ai"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

locals {
  name_prefix = "${var.project}-${var.environment}"
}

output "name_prefix" {
  description = "Resource name prefix for this environment"
  value       = local.name_prefix
}
