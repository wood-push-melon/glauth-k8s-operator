# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "glauth-k8s"
}

variable "base" {
  description = "Charm base"
  type        = string
  default     = "ubuntu@22.04"
}

variable "channel" {
  description = "Charm channel"
  type        = string
  default     = "latest/stable"
}

variable "config" {
  description = "Charm configuration"
  type        = map(string)
  default     = {}
}

variable "constraints" {
  description = "Deployment constraints"
  type        = string
  default     = "arch=amd64"
}

variable "model_name" {
  description = "Model name"
  type        = string
}

variable "revision" {
  description = "Charm revision"
  type        = number
  nullable    = true
  default     = null
}

variable "units" {
  description = "Number of units"
  type        = number
  default     = 1
}
