"""Tests for *pluserable*."""

from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from unittest import TestCase

from paste.deploy.loadwsgi import appconfig
from pyramid import testing

from tests.models import Activation, User

INI_PATH = Path(__file__).parent / "test.ini"


class UnitTestCase(TestCase):
    """Base class for all our tests, especially unit tests."""

    def create_users(
        self, count=1, password="Please bypass hashing!", activation=False
    ):
        """Return a user if count is 1, else a list of users."""
        users = []
        for index in range(1, count + 1):
            user = User(
                username="sagan{}".format(index),
                email="carlsagan{}@nasa.gov".format(index),
                password=password,
                registered_date=datetime(2000, 1, 1),
                last_login_date=datetime(2000, 1, 1),
            )
            if activation:
                user.activation = Activation()
            users.append(user)
            if hasattr(self, "repo"):
                self.repo.add(user)
        if count == 1:
            return users[0]
        else:
            return users


def _make_eko(sas_factory=None):
    from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
    from kerno.start import Eko

    eko = Eko.from_ini(str(INI_PATH))
    if sas_factory:
        eko.utilities.register(BaseSQLAlchemyRepository.SAS, sas_factory)
    eko.include("pluserable")
    return eko


class AppTestCase(UnitTestCase):
    """Base class providing a configured Pyramid app.

    For integration tests and slow functional tests.
    """

    @classmethod
    def _read_pyramid_settings(cls):
        return appconfig("config:" + str(INI_PATH))

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
        cls.engine = engine_from_config(cls.settings, prefix="sqlalchemy.")
        print("Creating the tables on the test database:\n%s" % cls.engine)
        Base.metadata.drop_all(cls.engine)
        Base.metadata.create_all(cls.engine)

    def setUp(self):
        """Prepare for each individual test."""
        self.kerno = _make_eko().kerno

    def get_request(self, post=None, request_method="GET"):
        """Return a dummy request for testing."""
        if post is None:
            post = {"csrf_token": "irrelevant but required"}
        request = testing.DummyRequest(post)
        request.client_addr = "127.0.0.1"
        request.session = Mock()
        request.method = request_method
        request.repo = self.repo
        request.kerno = self.kerno
        return request
