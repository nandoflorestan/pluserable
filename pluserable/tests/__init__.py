"""Tests for *pluserable*."""

from unittest import TestCase
from pkg_resources import resource_filename
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from pluserable.web.pyramid import find_or_create_mundi
from pluserable.tests.models import Activation, User, Group
from pluserable.interfaces import (
    IDBSession, IUserClass, IActivationClass, IGroupClass)


class PluserableTestCase(TestCase):
    """Base class for all our tests, especially unit tests."""

    def create_users(self, count=1, activation=False):
        """Return a user if count is 1, else a list of users."""
        users = []
        for index in range(1, count + 1):
            user = User(username='sagan{}'.format(index),
                        email='carlsagan{}@nasa.org'.format(index),
                        password='science')
            if activation:
                user.activation = Activation()
            users.append(user)
        if hasattr(self, 'sas'):
            self.sas.add_all(users)
        if count == 1:
            return users[0]
        else:
            return users


class AppTestCase(PluserableTestCase):
    """Base class providing a configured Pyramid app.

    For integration tests and slow functional tests.
    """

    @classmethod
    def _read_pyramid_settings(cls, kind=''):
        if kind:
            kind = kind + '/'
        return appconfig(
            'config:' + resource_filename(__name__, kind + 'test.ini'))

    def _initialize_config(self, settings, session_factory):
        config = testing.setUp(settings=settings)
        registry = config.registry
        find_or_create_mundi(registry)
        registry.registerUtility(session_factory, IDBSession)

        # TODO REMOVE:
        # registry.registerUtility(Activation, IActivationClass)
        # registry.registerUtility(User, IUserClass)
        # registry.registerUtility(Group, IGroupClass)
        return config
