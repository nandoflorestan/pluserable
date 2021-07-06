"""Test groupfinder and request.user."""

from datetime import datetime
from unittest.mock import Mock

from pluserable.web.pyramid import get_user

from tests.integration import IntegrationTestBase


class TestInitCase(IntegrationTestBase):  # noqa

    def test_get_user_fetches_existing_user(self):
        """Fake an authenticated user and see if it appears as request.user."""
        the_user = self.create_users(count=1)
        self.repo.flush()
        request = Mock()
        request.repo = self.get_request().repo
        request.unauthenticated_userid = 1
        user = get_user(request)
        assert user is the_user
        assert user.registered_date == datetime(2000, 1, 1)
        assert user.last_login_date == datetime(2000, 1, 1)
