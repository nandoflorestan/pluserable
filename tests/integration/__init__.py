"""An integration test goes through several layers of production code.

It accesses a database, so it is slower than a unit test.
"""

from mock import Mock
from bag.sqlalchemy.tricks import SubtransactionTrick
from pyramid import testing
from sqlalchemy.orm import sessionmaker
from pluserable.data.repository import instantiate_repository
from tests import AppTestCase


class IntegrationTestBase(AppTestCase):
    """Enclose each test in a subtransaction and roll it back."""

    def setUp(self):
        """Set up each test."""
        self.subtransaction = SubtransactionTrick(
            engine=self.engine, sessionmaker=sessionmaker)
        self.sas = self.subtransaction.sas  # TODO REMOVE

        def sas_factory():
            return self.subtransaction.sas

        self.config = self._initialize_config(self.settings, sas_factory)
        self.config.include('pluserable')
        self.repo = instantiate_repository(self.config.registry)

    def tearDown(self):
        """Executed after each test."""
        testing.tearDown()
        self.subtransaction.close()

    def get_request(self, post=None, request_method='GET'):
        """Return a dummy request for testing."""
        if post is None:
            post = {}
        request = testing.DummyRequest(post)
        request.session = Mock()
        request.method = request_method
        request.replusitory = self.repo
        return request
