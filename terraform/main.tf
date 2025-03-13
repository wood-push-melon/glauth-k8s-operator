# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "glauth-k8s" {
  name  = var.app_name
  model = var.model_name
  trust = true

  charm {
    name     = "glauth-k8s"
    base     = var.base
    channel  = var.channel
    revision = var.revision
  }

  config      = var.config
  constraints = var.constraints
  units       = var.units
}
