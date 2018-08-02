# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import os

import pytest
from neomodel import config as neomodel_config, db as neo4j_db

from estuary_updater.consumer import EstuaryUpdater


neomodel_config.DATABASE_URL = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:neo4j@localhost:7687')
neomodel_config.AUTO_INSTALL_LABELS = True


# Reinitialize Neo4j before each test
@pytest.fixture(autouse=True)
def run_before_tests():
    """Pytest fixture that prepares the environment before each test."""
    # Code that runs before each test
    neo4j_db.cypher_query('MATCH (a) DETACH DELETE a')


@pytest.fixture(scope='session')
def consumer():
    """Pytest fixture that creates an EstuaryUpdater instance."""
    class FakeHub(object):
        """FakeHub to used to initialize a fedmsg consumer."""

        config = {}

    return EstuaryUpdater(FakeHub())


@pytest.fixture
def mock_build_one():
    """Return a mock build in the format of koji.ClientSession.getBuild."""
    return {
        'completion_ts': 1529094398.0,
        'creation_ts': 1529094038.0,
        'epoch': 'epoch',
        'extra': {'container_koji_task_id': 17511743},
        'id': 710916,
        'name': 'e2e-container-test-product-container',
        'package_name': 'e2e-container-test-product-container',
        'owner_name': 'emusk',
        'release': '36.1528968216',
        'version': '7.4',
        'start_ts': 1529094098.0,
        'state': 0
    }


@pytest.fixture
def mock_build_two():
    """Return a mock build in the format of koji.ClientSession.getBuild."""
    return {
        'completion_ts': 1529094398.0,
        'creation_ts': 1529094038.0,
        'epoch': 'epoch',
        'extra': {'container_koji_task_id': 17511743},
        'id': 123456,
        'name': 'e2e-container-test-product-container',
        'package_name': 'e2e-container-test-product-container',
        'owner_name': 'emusk',
        'release': '37.1528968216',
        'version': '8.4',
        'start_ts': 1529094098.0,
        'state': 0
    }


@pytest.fixture
def mock_build_three():
    """Return a mock build in the format of koji.ClientSession.getBuild."""
    return {
        'completion_ts': 1529094398.0,
        'creation_ts': 1529094038.0,
        'epoch': 'epoch',
        'extra': {'container_koji_task_id': 17511743},
        'id': 234567,
        'name': 'e2e-container-test-product-container',
        'package_name': 'e2e-container-test-product-container',
        'owner_name': 'emusk',
        'release': '38.1528968216',
        'version': '9.4',
        'start_ts': 1529094098.0,
        'state': 0
    }
