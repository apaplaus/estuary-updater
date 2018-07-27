# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import json
from os import path
import datetime

from estuary.models.errata import Advisory
from estuary.models.koji import KojiBuild
from estuary.models.user import User
import requests
import mock
import pytz

from estuary_updater.handlers.errata import ErrataHandler
from estuary_updater import config
from tests import message_dir


def test_activity_status_handler():
    """Test the errata handler when it receives a new activity status message."""
    with open(path.join(message_dir, 'errata', 'errata_api.json'), 'r') as f:
        errata_api_msg = json.load(f)
    url = 'https://errata.domain.com/api/v1/erratum/34661'
    with mock.patch('requests.get') as mock_get:
        mock_response = mock.Mock()
        mock_response.json.return_value = errata_api_msg
        mock_get.return_value = mock_response
        requests.get(url).json()
        with open(path.join(message_dir, 'errata', 'activity_status.json'), 'r') as f:
            msg = json.load(f)
        assert ErrataHandler.can_handle(msg) is True
        handler = ErrataHandler(config)
        handler.handle(msg)
        advisory = Advisory.nodes.get_or_none(id_='34661')
        assert advisory is not None

        assert advisory.actual_ship_date is None
        assert advisory.advisory_name == 'RHEA-2018:34661-01'
        assert advisory.content_types == ['rpm']
        assert advisory.created_at == datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc)
        assert advisory.issue_date == datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc)
        assert advisory.product_short_name == 'RHEL'
        assert advisory.release_date is None
        assert advisory.security_impact == 'None'
        assert advisory.security_sla is None
        assert advisory.status_time == datetime.datetime(2018, 7, 3, 14, 15, 40, tzinfo=pytz.utc)
        assert advisory.synopsis == 'libvirt-python bug fix and enhancement update'
        assert advisory.update_date == datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc)


@mock.patch('koji.ClientSession')
def test_builds_added_handler(mock_koji_cs):
    """Test the Errata handler when it receives a new builds added message."""
    mock_koji_session = mock.Mock()
    mock_koji_session.getBuild.return_value = {
        'completion_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'creation_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'epoch': 'epoch',
        'extra': 'extra',
        'id': 123456,
        'package_name': 'openstack-zaqar-container',
        'owner_name': 'emusk',
        'version': '13.0',
        'release': '45',
        'start_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'state': 1
    }
    mock_koji_cs.return_value = mock_koji_session

    advisory = Advisory.get_or_create({'id_': '34983'})[0]

    with open(path.join(message_dir, 'errata', 'builds_added.json'), 'r') as f:
        msg = json.load(f)
    # Make sure the handler can handle the message
    assert ErrataHandler.can_handle(msg) is True
    # Instantiate the handler
    handler = ErrataHandler(config)
    # Run the handler
    handler.handle(msg)

    build = KojiBuild.nodes.get_or_none(id_=123456)
    owner = User.nodes.get_or_none(username='emusk')
    assert build is not None
    assert build.name == 'openstack-zaqar-container'
    assert build.version == '13.0'
    assert build.release == '45'
    assert build.completion_time == datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc)
    assert build.creation_time == datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc)
    assert build.epoch == 'epoch'
    assert build.extra == 'extra'
    assert build.id_ == '123456'
    assert build.start_time == datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc)
    assert build.state == 1

    assert advisory.attached_builds.is_connected(build)
    assert build.owner.is_connected(owner)


@mock.patch('koji.ClientSession')
def test_builds_removed_handler(mock_koji_cs):
    """Test the Errata handler when it receives a new builds removed message."""
    mock_koji_session = mock.Mock()
    mock_koji_session.getBuild.return_value = {
        'completion_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'creation_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'epoch': 'epoch',
        'extra': 'extra',
        'id': 123456,
        'package_name': 'openstack-zaqar-container',
        'owner_name': 'emusk',
        'version': '13.0',
        'release': '45',
        'start_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'state': 1
    }
    mock_koji_cs.return_value = mock_koji_session

    advisory = Advisory.get_or_create({'id_': '34983'})[0]
    build = KojiBuild.get_or_create({
        'completion_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'creation_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'epoch': 'epoch',
        'extra': 'extra',
        'id_': '123456',
        'package_name': 'openstack-zaqar-container',
        'owner_name': 'emusk',
        'version': '13.0',
        'release': '45',
        'start_time': datetime.datetime(2018, 6, 15, 15, 26, 38, tzinfo=pytz.utc),
        'state': 1
    })[0]

    advisory.attached_builds.connect(build)

    with open(path.join(message_dir, 'errata', 'builds_removed.json'), 'r') as f:
        msg = json.load(f)
    # Make sure the handler can handle the message
    assert ErrataHandler.can_handle(msg) is True
    # Instantiate the handler
    handler = ErrataHandler(config)
    # Run the handler
    handler.handle(msg)

    assert advisory is not None
    assert build is not None

    assert not advisory.attached_builds.is_connected(build)
