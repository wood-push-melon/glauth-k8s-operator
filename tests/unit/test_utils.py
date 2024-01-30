# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from io import StringIO
from unittest.mock import MagicMock, PropertyMock, patch, sentinel

from constants import DATABASE_INTEGRATION_NAME, WORKLOAD_CONTAINER
from ops.charm import CharmBase, HookEvent
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
from ops.testing import Harness
from utils import (
    after_config_updated,
    block_on_missing,
    demand_tls_certificates,
    leader_unit,
    validate_container_connectivity,
    validate_database_resource,
    validate_integration_exists,
)


class TestUtils:
    def test_leader_unit(self, harness: Harness) -> None:
        @leader_unit
        def wrapped_func(charm: CharmBase) -> sentinel:
            return sentinel

        assert wrapped_func(harness.charm) is sentinel

    def test_not_leader_unit(self, harness: Harness) -> None:
        @leader_unit
        def wrapped(charm: CharmBase) -> sentinel:
            return sentinel

        harness.set_leader(False)

        assert wrapped(harness.charm) is None

    def test_container_connected(self, harness: Harness, mocked_hook_event: MagicMock) -> None:
        @validate_container_connectivity
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        harness.set_can_connect(WORKLOAD_CONTAINER, True)

        assert wrapped(harness.charm, mocked_hook_event) is sentinel

    def test_container_not_connected(self, harness: Harness, mocked_hook_event: MagicMock) -> None:
        @validate_container_connectivity
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        harness.set_can_connect(WORKLOAD_CONTAINER, False)

        assert wrapped(harness.charm, mocked_hook_event) is None
        assert isinstance(harness.model.unit.status, WaitingStatus)

    def test_when_relation_exists_with_block_request(
        self,
        harness: Harness,
        database_relation: int,
        mocked_hook_event: MagicMock,
    ) -> None:
        @validate_integration_exists(DATABASE_INTEGRATION_NAME, on_missing=block_on_missing)
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is sentinel

    def test_when_relation_not_exists_with_block_request(
        self, harness: Harness, mocked_hook_event: MagicMock
    ) -> None:
        @validate_integration_exists(DATABASE_INTEGRATION_NAME, on_missing=block_on_missing)
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is None
        assert isinstance(harness.model.unit.status, BlockedStatus)

    def test_when_relation_not_exists_without_request(
        self, harness: Harness, mocked_hook_event: MagicMock
    ) -> None:
        harness.model.unit.status = ActiveStatus()

        @validate_integration_exists(DATABASE_INTEGRATION_NAME)
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is None
        assert isinstance(harness.model.unit.status, ActiveStatus)

    def test_database_resource_created(
        self, harness: Harness, database_resource: MagicMock, mocked_hook_event: MagicMock
    ) -> None:
        @validate_database_resource
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is sentinel

    def test_database_resource_not_created(
        self, harness: Harness, mocked_hook_event: MagicMock
    ) -> None:
        @validate_database_resource
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is None
        assert isinstance(harness.model.unit.status, WaitingStatus)

    def test_tls_certificates_not_exist(
        self,
        mocked_tls_certificates: MagicMock,
        harness: Harness,
        mocked_hook_event: MagicMock,
    ) -> None:
        @demand_tls_certificates
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            charm.unit.status = ActiveStatus()
            return sentinel

        mocked_tls_certificates.return_value = False
        assert wrapped(harness.charm, mocked_hook_event) is None
        assert isinstance(harness.model.unit.status, BlockedStatus)

    def test_demand_tls_certificates(
        self,
        harness: Harness,
        mocked_hook_event: MagicMock,
        mocked_tls_certificates: MagicMock,
    ) -> None:
        @demand_tls_certificates
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is sentinel

    @patch("ops.model.Container.pull", return_value=StringIO("abc"))
    @patch("charm.ConfigFile.content", new_callable=PropertyMock, return_value="abc")
    def test_after_config_updated(
        self,
        mocked_container_pull: MagicMock,
        mocked_configfile_content: MagicMock,
        harness: Harness,
        mocked_hook_event: MagicMock,
    ) -> None:
        @after_config_updated
        def wrapped(charm: CharmBase, event: HookEvent) -> sentinel:
            charm.unit.status = ActiveStatus()
            return sentinel

        assert wrapped(harness.charm, mocked_hook_event) is sentinel
        assert isinstance(harness.model.unit.status, ActiveStatus)
