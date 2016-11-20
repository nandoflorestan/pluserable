"""Tests for *pluserable*."""

from unittest import TestCase
from pkg_resources import resource_filename
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from pluserable.tests.models import Activation, User, Group
from pluserable.interfaces import (
    IDBSession, IUserClass, IActivationClass, IGroupClass)


class PluserableTestCase(TestCase):
    """Base class for all our tests."""

    @classmethod
    def _read_pyramid_settings(cls, kind=''):
        if kind:
            kind = kind + '/'
        return appconfig(
            'config:' + resource_filename(__name__, kind + 'test.ini'))

    def make_test_app(self, settings, session_factory):
        config = testing.setUp(settings=settings)
        registry = config.registry
        registry.registerUtility(session_factory, IDBSession)
        registry.registerUtility(Activation, IActivationClass)
        registry.registerUtility(User, IUserClass)
        registry.registerUtility(Group, IGroupClass)
        return config
