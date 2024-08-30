# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import functools
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Optional

import aiofiles
import ldap.ldapobject
import psycopg
import pytest_asyncio
import yaml
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from pytest_operator.plugin import OpsTest

from constants import GLAUTH_LDAP_PORT

METADATA = yaml.safe_load(Path("./charmcraft.yaml").read_text())
CERTIFICATE_PROVIDER_APP = "self-signed-certificates"
DB_APP = "postgresql-k8s"
GLAUTH_PROXY = "ldap-proxy"
GLAUTH_APP = METADATA["name"]
GLAUTH_IMAGE = METADATA["resources"]["oci-image"]["upstream-source"]
GLAUTH_CLIENT_APP = "any-charm"


@contextmanager
def ldap_connection(uri: str, bind_dn: str, bind_password: str) -> ldap.ldapobject.LDAPObject:
    conn = ldap.initialize(uri)
    try:
        conn.simple_bind_s(bind_dn, bind_password)
        yield conn
    finally:
        conn.unbind_s()


def extract_certificate_common_name(certificate: str) -> Optional[str]:
    cert_data = certificate.encode()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    if not (rdns := cert.subject.rdns):
        return None

    return rdns[0].rfc4514_string()


async def get_secret(ops_test: OpsTest, secret_id: str) -> dict:
    show_secret_cmd = f"show-secret {secret_id} --reveal".split()
    _, stdout, _ = await ops_test.juju(*show_secret_cmd)
    cmd_output = yaml.safe_load(stdout)
    return cmd_output[secret_id]


async def get_unit_data(ops_test: OpsTest, unit_name: str) -> dict:
    show_unit_cmd = f"show-unit {unit_name}".split()
    _, stdout, _ = await ops_test.juju(*show_unit_cmd)
    cmd_output = yaml.safe_load(stdout)
    return cmd_output[unit_name]


async def get_integration_data(
    ops_test: OpsTest, app_name: str, integration_name: str, unit_num: int = 0
) -> Optional[dict]:
    data = await get_unit_data(ops_test, f"{app_name}/{unit_num}")
    return next(
        (
            integration
            for integration in data["relation-info"]
            if integration["endpoint"] == integration_name
        ),
        None,
    )


async def get_app_integration_data(
    ops_test: OpsTest,
    app_name: str,
    integration_name: str,
    unit_num: int = 0,
) -> Optional[dict]:
    data = await get_integration_data(ops_test, app_name, integration_name, unit_num)
    return data["application-data"] if data else None


async def get_unit_integration_data(
    ops_test: OpsTest,
    app_name: str,
    remote_app_name: str,
    integration_name: str,
) -> Optional[dict]:
    data = await get_integration_data(ops_test, app_name, integration_name)
    return data["related-units"][f"{remote_app_name}/0"]["data"] if data else None


@pytest_asyncio.fixture
async def app_integration_data(ops_test: OpsTest) -> Callable:
    return functools.partial(get_app_integration_data, ops_test)


@pytest_asyncio.fixture
async def unit_integration_data(ops_test: OpsTest) -> Callable:
    return functools.partial(get_unit_integration_data, ops_test)


@pytest_asyncio.fixture
async def ldap_integration_data(app_integration_data: Callable) -> Optional[dict]:
    return await app_integration_data(GLAUTH_CLIENT_APP, "ldap")


@pytest_asyncio.fixture
async def database_integration_data(app_integration_data: Callable) -> Optional[dict]:
    return await app_integration_data(GLAUTH_APP, "pg-database")


@pytest_asyncio.fixture
async def certificate_integration_data(app_integration_data: Callable) -> Optional[dict]:
    return await app_integration_data(GLAUTH_APP, "certificates")


@pytest_asyncio.fixture
async def ldap_configurations(
    ops_test: OpsTest, ldap_integration_data: Optional[dict]
) -> Optional[tuple[str, ...]]:
    if not ldap_integration_data:
        return None

    base_dn = ldap_integration_data["base_dn"]
    bind_dn = ldap_integration_data["bind_dn"]
    bind_password_secret: str = ldap_integration_data["bind_password_secret"]

    prefix, _, secret_id = bind_password_secret.partition(":")
    bind_password = await get_secret(ops_test, secret_id or prefix)

    return base_dn, bind_dn, bind_password["content"]["password"]


async def unit_address(ops_test: OpsTest, *, app_name: str, unit_num: int = 0) -> str:
    status = await ops_test.model.get_status()
    return status["applications"][app_name]["units"][f"{app_name}/{unit_num}"]["address"]


@pytest_asyncio.fixture
async def ldap_uri(ops_test: OpsTest) -> str:
    address = await unit_address(ops_test, app_name=GLAUTH_APP)
    return f"ldap://{address}:{GLAUTH_LDAP_PORT}"


@pytest_asyncio.fixture
async def database_address(ops_test: OpsTest) -> str:
    return await unit_address(ops_test, app_name=DB_APP)


@pytest_asyncio.fixture
async def initialize_database(
    database_integration_data: Optional[dict], database_address: str
) -> None:
    assert database_integration_data is not None, "database_integration_data should be ready"

    db_connection_params = {
        "dbname": database_integration_data["database"],
        "user": database_integration_data["username"],
        "password": database_integration_data["password"],
        "host": database_address,
        "port": 5432,
    }

    async with await psycopg.AsyncConnection.connect(**db_connection_params) as conn:
        async with conn.cursor() as cursor:
            async with aiofiles.open("tests/integration/db.sql", "rb") as f:
                statements = await f.read()

            await cursor.execute(statements)
            await conn.commit()
