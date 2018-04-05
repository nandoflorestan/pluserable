"""Test groupfinder and request.user."""

from datetime import datetime
from mock import Mock, patch
from pluserable import groupfinder
from pluserable.web.pyramid import get_user
from tests.models import Group
from . import IntegrationTestBase


class TestInitCase(IntegrationTestBase):

    def test_get_user_fetches_existing_user(self):
        """Fake an authenticated user and see if it appears as request.user."""
        the_user = self.create_users(count=1)
        self.repo.flush()
        with patch('pluserable.web.pyramid.unauthenticated_userid') as unauth:
            unauth.return_value = 1
            request = self.get_request()
            got = get_user(request)
            assert got is the_user
            assert got.registered_date == datetime(2000, 1, 1)
            assert got.last_login_date == datetime(2000, 1, 1)

    def test_groupfinder(self):
        user1 = self.create_users(count=1)
        group = Group(name='foo', description='bar')
        group.users.append(user1)
        self.sas.flush()

        request = Mock()
        request.user = user1

        results = groupfinder(1, request)

        assert 'group:foo' in results
        assert 'user:%s' % (user1.id) in results
        assert len(results) == 2

    def test_groupfinder_no_groups(self):
        user1, user2 = self.create_users(count=2)
        group = Group(name='foo', description='bar')
        group.users.append(user1)
        self.sas.flush()

        request = Mock()
        request.user = user2

        results = groupfinder(2, request)

        assert len(results) == 1
        assert 'user:%s' % (user2.id) in results
