"""Tests for *pluserable*."""

from datetime import datetime
from mock import Mock
from unittest import TestCase

from pkg_resources import resource_filename
from paste.deploy.loadwsgi import appconfig
from pyramid import testing

from pluserable import const
from pluserable.settings import get_default_pluserable_settings

from tests.models import Activation, User


class UnitTestCase(TestCase):
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


def _make_eko(sas_factory=None):
    from bag.settings import SettingsReader
    from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
    from kerno.start import Eko
    eko = Eko.from_ini(_get_ini_path())
    if sas_factory:
        eko.utilities.register(BaseSQLAlchemyRepository.SAS, sas_factory)

    eko.include('kerno.repository')  # adds add_repository_mixin() to eko
    eko.kerno.pluserable_settings = SettingsReader(
        get_default_pluserable_settings())
    # eko.include('pluserable')

    eko.utilities.set_default(
        const.REPOSITORY, 'pluserable.data.sqlalchemy.repository:Repository')
    eko.add_repository_mixin(  # type: ignore
        mixin=eko.kerno.utilities[const.REPOSITORY],  # type: ignore
    )

    return eko


class AppTestCase(UnitTestCase):
    """Base class providing a configured Pyramid app.

    For integration tests and slow functional tests.
    """

    @classmethod
    def _read_pyramid_settings(cls, kind=''):
        return appconfig('config:' + _get_ini_path(kind=kind))

    run_once = False

    @classmethod
    def setUpClass(cls):
        """Create test database and tables when some tests start running."""
        if AppTestCase.run_once:
            return  # Only create tables once per test suite run
        AppTestCase.run_once = True
        cls.create_test_database()

    @classmethod
    def create_test_database(cls):
        """Create tables once to run all the tests."""
        from sqlalchemy import engine_from_config
        from tests.models import Base

        cls = AppTestCase  # set class variables on superclass
        cls.settings = cls._read_pyramid_settings()
        cls.engine = engine_from_config(cls.settings, prefix='sqlalchemy.')
        print('Creating the tables on the test database:\n%s' % cls.engine)
        Base.metadata.drop_all(cls.engine)
        Base.metadata.create_all(cls.engine)

    def setUp(self):
        """Prepare for each individual test."""
        self.kerno = _make_eko().kerno

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
        return request
