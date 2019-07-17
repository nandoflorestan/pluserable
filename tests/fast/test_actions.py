"""Unit tests for pure methods of actions (pure business rules)."""

from mock import Mock
from pluserable.actions import CheckCredentials
from pluserable.exceptions import AuthenticationFailure
from . import FastTestCase


class TestCheckCredentials(FastTestCase):
    """Unit tests for the _check_credentials() method."""

    def _test(self, password=None, activation=False):
        user = self.create_users(count=1, activation=activation)
        action = Mock()
        action._require_activation = True
        return user, CheckCredentials._check_credentials(
            self=action, user=user, handle=user.username,
            password=password or 'science')

    def test_with_bad_password_raises(self):  # noqa
        with self.assertRaises(AuthenticationFailure):
            self._test(password='wrong')

    def test_with_ok_password_returns_user(self):  # noqa
        user, ret = self._test()
        assert ret is user

    def test_with_pending_activation_raises(self):  # noqa
        with self.assertRaises(AuthenticationFailure):
            self._test(activation=True)
