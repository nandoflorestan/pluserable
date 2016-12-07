"""Unit tests for pure methods of actions (pure business rules)."""

from pluserable.actions import CheckCredentials
from pluserable.exceptions import AuthenticationFailure
from . import FakeKerno, FastTestCase


class TestCheckCredentials(FastTestCase):
    """Unit tests for _check_credentials()."""

    def _make_one(self, activation=False):
        user = self.create_users(count=1, activation=activation)
        action = CheckCredentials(  # Barely instantiate just to test a method
            registry=self._make_registry(), repository=None, user=user,
            payload={}, kerno=None)
        action.kerno = FakeKerno()
        return user, action

    def test_with_bad_password_raises(self):
        user, action = self._make_one()
        with self.assertRaises(AuthenticationFailure):
            action._check_credentials(user, user.email, password='wrong')

    def test_with_ok_password_returns_user(self):
        user, action = self._make_one()
        ret = action._check_credentials(user, user.email, password='science')
        assert ret is user

    def test_with_pending_activation_raises(self):
        user, action = self._make_one(activation=True)
        with self.assertRaises(AuthenticationFailure):
            action._check_credentials(user, user.email, password='science')
