"""Unit tests for pure methods of actions (pure business rules)."""

from unittest.mock import Mock
from pluserable.actions import CheckCredentials
from pluserable.exceptions import AuthenticationFailure
from . import FastTestCase


class TestCheckCredentials(FastTestCase):
    """Unit tests for the _check_credentials() method."""

    def _test(self, password="science", activation=False):
        user = self.create_users(
            count=1, activation=activation, password="science"
        )
        action = Mock()
        action._require_activation = True
        return user, CheckCredentials._check_credentials(
            self=action, user=user, handle=user.username, password=password
        )

    def test_with_bad_password_raises(self):  # noqa
        with self.assertRaises(AuthenticationFailure):
            self._test(password="wrong")

    def test_with_right_password_returns_user(self):  # noqa
        user, ret = self._test(password="science")
        assert ret is user

    def test_with_pending_activation_raises(self):  # noqa
        with self.assertRaises(AuthenticationFailure):
            self._test(activation=True, password="Please bypass hashing!")
