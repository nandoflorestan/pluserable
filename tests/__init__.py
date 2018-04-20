"""Tests for *pluserable*."""

from datetime import datetime
from mock import Mock
from unittest import TestCase
from pkg_resources import resource_filename
from paste.deploy.loadwsgi import appconfig
from pyramid import testing

from pluserable import const
from pluserable.data.repository import instantiate_repository
from tests.models import Activation, User


class PluserableTestCase(TestCase):
    """Base class for all our tests, especially unit tests."""

    def create_users(self, count=1, activation=False):
        """Return a user if count is 1, else a list of users."""
        users = []
        for index in range(1, count + 1):
            user = User(username='sagan{}'.format(index),
                        email='carlsagan{}@nasa.gov'.format(index),
                        password='science',
                        registered_date=datetime(2000, 1, 1),
                        last_login_date=datetime(2000, 1, 1),
                        )
            if activation:
                user.activation = Activation()
            users.append(user)
            if hasattr(self, 'repo'):
                self.repo.store_user(user)
        if count == 1:
            return users[0]
        else:
            return users


def _get_ini_path(kind=''):
    if kind:
        kind = kind + '/'
    path = resource_filename(__name__, kind + 'test.ini')
    return path


class AppTestCase(PluserableTestCase):
    """Base class providing a configured Pyramid app.

    For integration tests and slow functional tests.
    """

    @classmethod
    def _read_pyramid_settings(cls, kind=''):
        return appconfig('config:' + _get_ini_path(kind=kind))

    def _initialize_config(self, settings):
        config = testing.setUp(settings=settings)
        return config

    run_once = False

    @classmethod
    def setUpClass(cls):
        """Create test database and tables when some tests start running."""
        if AppTestCase.run_once:
            return  # Only create tables once per test suite run
        AppTestCase.run_once = True

        from py.test import config

        # Only run database setup on master (in case of xdist/multiproc mode)
        if not hasattr(config, 'slaveinput'):
            from sqlalchemy import engine_from_config
            from tests.models import Base

            cls = AppTestCase  # set class variables on superclass
            cls.settings = cls._read_pyramid_settings()
            cls.engine = engine_from_config(cls.settings, prefix='sqlalchemy.')
            print('Creating the tables on the test database:\n%s' % cls.engine)
            Base.metadata.drop_all(cls.engine)
            Base.metadata.create_all(cls.engine)

    def start_kerno(self, config, sas_factory=None):
        eko = config.get_eko()
        eko.register_utility(const.SAS, sas_factory or self.sas)
        self.repo = instantiate_repository(config.registry)
        self.kerno = eko.kerno

    def get_request(self, post=None, request_method='GET'):
        """Return a dummy request for testing."""
        if post is None:
            post = {'csrf_token': 'irrelevant but required'}
        request = testing.DummyRequest(post)
        request.session = Mock()
        request.method = request_method
        request.repo = self.repo
        request.user = None
        request.kerno = self.kerno

        # from tests.fast import FakeKerno
        # request.kerno = FakeKerno()

        return request
