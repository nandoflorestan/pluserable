"""Unit tests for pure methods of actions (pure business rules)."""

from pluserable.actions import PluserableAction
from pluserable.exceptions import AuthenticationFailure
from . import FastTestCase

# TODO Actions must follow the Mundi Action pattern


class TestCheckCredentials(FastTestCase):
    """Unit tests for _check_credentials()."""

    def test_with_bad_password_raises(self):
        user = self.create_users(count=1)
        action = PluserableAction(self._make_registry(), repository=None)
        with self.assertRaises(AuthenticationFailure):
            action._check_credentials(user, user.email, password='wrong')

    def test_with_ok_password_returns_user(self):
        user = self.create_users(count=1)
        action = PluserableAction(self._make_registry(), repository=None)
        ret = action._check_credentials(user, user.email, password='science')
        assert ret is user

    def test_with_pending_activation_raises(self):
        user = self.create_users(count=1)
        user.activation_id = 42
        action = PluserableAction(self._make_registry(), repository=None)
        with self.assertRaises(AuthenticationFailure):
            action._check_credentials(user, user.email, password='science')
