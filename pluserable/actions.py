"""The **action** layer is also called "service" layer.

It stands between the model layer and the view layer.
It is the heart of an application and contains its business rules.

This is because MVC/MVT is insufficient for large apps. Views should
be thin.  Business rules must be decoupled from the web framework.
"""

from datetime import datetime
from bag.reify import reify
from kerno.action import Action
from kerno.state import MalbonaRezulto, Rezulto
from pluserable.exceptions import AuthenticationFailure
from pluserable.strings import get_strings
from typing import Any


class PluserableAction(Action):
    """Base class for our actions."""

    @reify
    def _strings(self):
        return get_strings(self.kerno)


def require_activation_setting_value(kerno) -> bool:
    """Return the value of a certain setting."""
    return kerno.pluserable_settings.bool('require_activation', default=True)


class CheckCredentials(PluserableAction):
    """Business rules decoupled from the web framework and from persistence."""

    @reify
    def _require_activation(self):
        return require_activation_setting_value(self.kerno)

    def q_user(self, handle: str) -> Any:
        """Fetch user. ``handle`` can be a username or an email."""
        if '@' in handle:
            return self.repo.q_user_by_email(handle)
        else:
            return self.repo.q_user_by_username(handle)

    def __call__(self, handle: str, password: str) -> Rezulto:
        """Get user object if credentials are valid, else raise."""
        r = Rezulto()  # type: Any
        r.user = self.q_user(handle)  # IO
        self._check_credentials(r.user, handle, password)  # might raise
        r.user.last_login_date = datetime.utcnow()
        return r

    def _check_credentials(self, user, handle: str, password: str):
        """Pure method (no IO) that checks credentials against ``user``."""
        if not user or not user.check_password(password):
            raise AuthenticationFailure(
                self._strings.wrong_email if '@' in handle
                else self._strings.wrong_username)

        if self._require_activation and not user.is_activated:
            raise AuthenticationFailure(self._strings.inactive_account)
        return user


class ActivateUser(PluserableAction):

    def __call__(self, code: str, user_id: int) -> Rezulto:
        """Find code, ensure belongs to user, delete activation instance."""
        activation = self.repo.q_activation_by_code(code)
        # TODO Put these strings away
        if not activation:
            raise MalbonaRezulto(
                status_int=404, title='Code not found',
                plain='That code cannot be found in the system. Maybe you '
                'already used it -- in this case, just try logging in.')

        user = self.repo.q_user_by_id(user_id)
        if not user:
            raise MalbonaRezulto(
                status_int=404, title='User not found',
                plain='That user cannot be found in the system.')

        if user.activation is not activation:
            raise MalbonaRezulto(
                status_int=404, title='Code and user do not match',
                plain='That code does not belong to that user.')

        self.repo.delete_activation(user, activation)
        ret = Rezulto()  # type: Any
        ret.user = user
        ret.activation = activation

        # TODO My current flash messages do not display titles
        # ret.add_message(
        #     title=self._strings.activation_email_verified_title,
        #     plain=self._strings.activation_email_verified)
        return ret
