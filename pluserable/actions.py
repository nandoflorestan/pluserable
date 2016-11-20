"""The **action** layer is also called "service" layer.

It stands between the model layer and the view layer.
It is the heart of an application and contains its business rules.

This is because MVC/MVT is insufficient for large apps. Views should
be thin.  Business rules must be decoupled from the web framework.
"""

from bag.settings import SettingsReader
from pyramid.decorator import reify
from pluserable.exceptions import AuthenticationFailure
from pluserable.repository import instantiate_repository
from pluserable.strings import get_strings


class PluserableAction(object):
    """Business rules decoupled from the web framework and from persistence."""

    def __init__(self, registry):
        """``registry`` is a zope.component registry or a Pyramid registry."""
        self.registry = registry

    @reify
    def _repo(self):
        return instantiate_repository(self.registry)

    @reify
    def _strings(self):
        return get_strings(self.registry)

    @reify
    def _settings_reader(self):
        return SettingsReader(self.registry.settings)

    @reify
    def _allow_inactive_login(self):
        return self._settings_reader.bool(
            'pluserable.allow_inactive_login', False)

    @reify
    def _require_activation(self):
        return self._settings_reader.bool(
            'pluserable.require_activation', True)

    def q_user(self, handle):
        """``handle`` can be a username or an email."""
        if '@' in handle:
            return self._repo.q_user_by_email(handle)
        else:
            return self._repo.q_user_by_username(handle)

    def check_credentials(self, handle, password):
        """Return user object if credentials are valid."""
        user = self.q_user(handle)
        return self._check_credentials(user, handle, password)

    def _check_credentials(self, user, handle, password):  # TODO unit test
        if not user or not user.check_password(password):
            raise AuthenticationFailure(
                self._strings.wrong_email if '@' in handle
                else self._strings.wrong_username)

        if not self._allow_inactive_login and self._require_activation \
                and not user.is_activated:
            raise AuthenticationFailure(self._strings.inactive_account)
        return user
