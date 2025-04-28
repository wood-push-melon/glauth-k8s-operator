# GLAuth Kubernetes Charmed Operator

[![CharmHub Badge](https://charmhub.io/glauth-k8s/badge.svg)](https://charmhub.io/glauth-k8s)
![Python](https://img.shields.io/python/required-version-toml?label=Python&tomlFilePath=https://raw.githubusercontent.com/canonical/glauth-k8s-operator/main/pyproject.toml)
[![Juju](https://img.shields.io/badge/Juju%20-3.0+-%23E95420)](https://github.com/juju/juju)
![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?label=Ubuntu&logo=ubuntu&logoColor=white)
[![License](https://img.shields.io/github/license/canonical/glauth-k8s-operator?label=License)](https://github.com/canonical/glauth-k8s-operator/blob/main/LICENSE)

[![Continuous Integration Status](https://github.com/canonical/glauth-k8s-operator/actions/workflows/on_push.yaml/badge.svg?branch=main)](https://github.com/canonical/glauth-k8s-operator/actions?query=branch%3Amain)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196.svg)](https://conventionalcommits.org)

This repository holds the Juju Kubernetes charmed operator
for [GLAuth](https://github.com/glauth/glauth), an open-sourced LDAP server.

## Usage

The `glauth-k8s` charmed operator can be deployed using the following command:

```shell
juju deploy glauth-k8s --channel edge --trust
```

The `glauth-k8s` charmed operator uses
the [Charmed PostgreSQL K8s Operator](https://github.com/canonical/postgresql-k8s-operator)
as the backend:

```shell
juju deploy postgresql-k8s --channel 14/stable --trust

juju integrate glauth-k8s postgresql-k8s
```

The `glauth-k8s` charmed operator also requires a certificate provider. Take
the `self-signed-certificates-operator` as an example:

```shell
juju deploy self-signed-certificates --channel stable --trust

juju integrate glauth-k8s self-signed-certificates
```

## Integrations

### `ldap` Integration

The `glauth-k8s` charmed operator offers the `ldap` integration with any
LDAP client charmed operator following
the [`ldap` interface protocol](https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/ldap/v0).

```shell
juju integrate <ldap-client-charm>:ldap glauth-k8s:ldap
```

### `glauth_auxiliary` Integration

The `glauth-k8s` charmed operator provides the `glauth_auxiliary`
integration with
the [`glauth-utils` charmed operator](https://github.com/canonical/glauth-utils)
to deliver necessary auxiliary configurations.

```shell
juju integrate glauth-utils glauth-k8s
```

### `certificate_transfer` Integration

The `glauth-k8s` charmed operator provides the `certificate_transfer`
integration with any charmed operator following the [`certificate_transfer`
interface protocol](https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/certificate_transfer/v0).

```shell
juju integrate <client-charm> glauth-k8s
```

### `postgresql_client` Integration

The `glauth-k8s` charmed operator requires the integration with the
`postgres-k8s` charmed operator following the [`postgresql_client` interface
protocol](https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/postgresql_client/v0).

```shell
juju integrate glauth-k8s postgresql-k8s
```

### `tls_certificates` Integration

The `glauth-k8s` charmed operator requires the `tls-certificates`
integration with any charmed operator following the [`tls_certificates`
interface protocol](https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/tls_certificates/v0).
Take the `self-signed-certificates-operator` as an example:

```shell
juju integrate glauth-k8s self-signed-certificates
```

## Observability

GLAuth operator integrates
with [Canonical Observability Stack (COS)](https://charmhub.io/topics/canonical-observability-stack)
bundle. It comes with a Grafana dashboard and Loki and Prometheus alert rules
for basic common scenarios. To integrate with the COS bundle, after
you [deploy](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s#heading--deploy-the-cos-lite-bundle)
it, you can run:

```shell
juju integrate glauth-k8s:metrics-endpoint prometheus:metrics-endpoint
juju integrate glauth-k8s:logging loki:logging
juju integrate glauth-k8s:grafana-dashboard grafana:grafana-dashboard
```

## Configurations

The `glauth-k8s` charmed operator offers the following charm configuration
options.

|  Charm Config Option   | Description                                                    | Example                                              |
|:----------------------:|----------------------------------------------------------------|------------------------------------------------------|
|       `base_dn`        | The portion of the DIT in which to search for matching entries | `juju config <charm-app> base-dn="dc=glauth,dc=com"` |
|   `starttls_enabled`   | The switch to enable/disable StartTLS support                  | `juju config <charm-app> starttls_enabled=true`      |
| `anonymousdse_enabled` | The switch to enable/disable anonymous access to the root DSE  | `juju config <charm-app> anonymousdse_enabled=true`  |

> ⚠️ **NOTE**
>
> - Please refer to the `charmcraft.yaml` for more details about the
    configurations.

## Security

Please see [SECURITY.md](https://github.com/canonical/glauth-k8s-operator/blob/main/SECURITY.md)
for guidelines on reporting security issues.

## Contributing

Please refer to the [Contributing](CONTRIBUTING.md) for developer guidance.
Please see the [Juju SDK documentation](https://juju.is/docs/sdk) for more
information about developing and improving charms.

## Licence

The GLAuth Kubernetes Charmed Operator is free software, distributed under the
Apache Software License, version 2.0.
See [LICENSE](https://github.com/canonical/glauth-k8s-operator/blob/main/LICENSE)
for more information.
