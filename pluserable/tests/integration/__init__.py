"""An integration test goes through several layers of production code.

It accesses a database, so it is slower than a unit test.
"""

from mock import Mock
from pyramid import testing
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from pluserable.tests import AppTestCase
from pluserable.tests.models import Base


class BaseTestCase(AppTestCase):

    @classmethod
    def setUpClass(cls):  # TODO MOVE TO ..
        cls.settings = settings = cls._read_pyramid_settings()
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()

    def setUp(self):
        self.connection = connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()
        Base.metadata.bind = connection

        # bind an individual Session to the connection
        self.sas = self.Session(bind=connection)

        def factory():
            return self.sas

        self.config = self._initialize_config(self.settings, factory)
        self.config.include('pluserable')

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.sas.close()
        self.connection.close()


class IntegrationTestBase(BaseTestCase):

    def get_request(self, post=None, request_method='GET'):
        if post is None:
            post = {}
        request = testing.DummyRequest(post)
        request.session = Mock()
        request.method = request_method
        return request
