"""Test request.user."""

from datetime import datetime

from pluserable.web.pyramid import get_user

from tests.integration import LoggedIntegrationTest


class TestInitCase(LoggedIntegrationTest):  # noqa

    def test_get_user_fetches_existing_user(self):
        """Fake an authenticated user and see if it appears as request.user."""
        request = self.get_request()
        assert request.unauthenticated_userid == 1
        assert request.identity
        user = get_user(request)
        assert user is request.identity
        assert user.registered_date == datetime(2000, 1, 1)
        assert user.last_login_date == datetime(2000, 1, 1)
