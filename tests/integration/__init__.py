"""An integration test goes through several layers of production code.

It accesses a database, so it is slower than a unit test.
"""

from bag.sqlalchemy.tricks import SubtransactionTrick
from pyramid import testing
from sqlalchemy.orm import sessionmaker
from pluserable import const
from pluserable.data.repository import instantiate_repository
from tests import AppTestCase, _get_ini_path


class IntegrationTestBase(AppTestCase):
    """Enclose each test in a subtransaction and roll it back."""

    def setUp(self):
        """Set up each test."""
        self.subtransaction = SubtransactionTrick(
            engine=self.engine, sessionmaker=sessionmaker)
        self.sas = self.subtransaction.sas  # TODO REMOVE

        def sas_factory():
            return self.subtransaction.sas

        self.config = self._initialize_config(self.settings)
        self.config.include('pluserable')
        self.config.setup_pluserable(_get_ini_path())
        self.start_kerno(self.config, sas_factory=sas_factory)

    def tearDown(self):
        """Clean up after each test."""
        testing.tearDown()
        self.subtransaction.close()
