import os
import unittest
from pkg_resources import resource_filename
from mock import Mock
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from pluserable.tests.models import Activation, Base, User, Group
from pluserable.interfaces import (
    IUserClass, IActivationClass, IGroupClass, IDBSession)

here = os.path.dirname(__file__)
# settings = appconfig('config:' + os.path.join(here, 'test.ini'))
settings = appconfig('config:' + resource_filename(__name__, 'test.ini'))

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()

    def setUp(self):
        self.config = testing.setUp()

        self.connection = connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        self.session = self.Session(bind=connection)

        def factory(registry):
            return self.session

        self.config.registry.registerUtility(factory, IDBSession)
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Group, IGroupClass)

        Base.metadata.bind = connection

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()
        self.connection.close()


class UnitTestBase(BaseTestCase):

    def get_request(self, post=None, request_method='GET'):
        if not post:
            post = {}
        request = testing.DummyRequest(post)
        request.session = Mock()
        request.method = request_method
        return request
