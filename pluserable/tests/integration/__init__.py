"""An integration test goes through several layers of production code.

It accesses a database, so it is slower than a unit test.
"""

from mock import Mock
from pyramid import testing
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from pluserable.repository import instantiate_repository
from pluserable.tests import AppTestCase
from pluserable.tests.models import Base


class BaseTestCase(AppTestCase):

    @classmethod
    def setUpClass(cls):  # TODO MOVE TO ..
        cls.settings = settings = cls._read_pyramid_settings()
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        """Set up each test."""
        self.sas = self.Session()

        def factory():
            return self.sas

        self.config = self._initialize_config(self.settings, factory)
        self.config.include('pluserable')

    def tearDown(self):
        """Roll back everything that happened with the session.

        session.commit() must never be called.
        """
        testing.tearDown()
        self.sas.rollback()
        self.sas.close()


class IntegrationTestBase(BaseTestCase):

    def get_request(self, post=None, request_method='GET'):
        if post is None:
            post = {}
        request = testing.DummyRequest(post)
        request.session = Mock()
        request.method = request_method
        request.replusitory = instantiate_repository(request.registry)
        return request
