# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

output "app_name" {
  value = juju_application.glauth-k8s.name
}

output "requires" {
  value = {
    pg-database  = "pg-database"
    logging      = "logging"
    certificates = "certificates"
    ingress      = "ingress"
    ldap-client  = "ldap-client"
  }
}

output "provides" {
  value = {
    metrics-endpoint  = "metrics-endpoint"
    grafana-dashboard = "grafana-dashboard"
    ldap              = "ldap"
    glauth-auxiliary  = "glauth-auxiliary"
    send-ca-cert      = "send-ca-cert"
  }
}