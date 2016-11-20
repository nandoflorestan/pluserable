"""Unit tests for pure methods of actions (pure business rules)."""

from pluserable.tests import PluserableTestCase
from pluserable.actions import PluserableAction

# TODO Actions must follow the Mundi Action pattern
# TODO Base for unit test classes


class TestCheckCredentials(PluserableTestCase):
    """Unit tests for _check_credentials()."""

    def test_with_ok_credentials_returns_user(self):
        _check_credentials(self, user, handle, password)

    def test_with_bad_username_raises(self):
        user = self.create_users(count=1)
        self.sas.flush()

        request = testing.DummyRequest()
        new_user = User.get_user(request, 'sagan', 'temp')
        assert new_user is None

    def test_with_bad_password_raises(self):
        raise NotImplementedError()
