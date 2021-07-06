"""An integration test goes through several layers of production code.

It accesses a database, so it is slower than a unit test.
"""

from bag.sqlalchemy.tricks import SubtransactionTrick
from kerno.web.pyramid import IKerno
from pyramid import testing
from sqlalchemy.orm import sessionmaker

from tests import AppTestCase, _make_eko


class IntegrationTestBase(AppTestCase):
    """Enclose each test in a subtransaction and roll it back."""

    def setUp(self):
        """Set up each test."""
        self.subtransaction = SubtransactionTrick(
            engine=self.engine, sessionmaker=sessionmaker
        )
        self.sas = self.subtransaction.sas  # TODO REMOVE

        def sas_factory():
            return self.subtransaction.sas

        self.kerno = _make_eko(sas_factory=sas_factory).kerno
        self.repo = self.kerno.new_repo()
        config = testing.setUp(settings=self.settings)
        config.registry.registerUtility(self.kerno, IKerno)
        config.include("pluserable")
        self.config = config
        self._config_pyramid_testing()

    def _config_pyramid_testing(self):
        pass

    def tearDown(self):
        """Clean up after each test."""
        testing.tearDown()
        self.subtransaction.close()


class LoggedIntegrationTest(IntegrationTestBase):
    """In tests of this class there is an authenticated user."""

    def _config_pyramid_testing(self):
        self.user = user = self.create_users()
        self.sas.flush()
        # https://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.testing_securitypolicy
        self.config.testing_securitypolicy(identity=user, userid=user.id)
