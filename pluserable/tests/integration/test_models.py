from datetime import datetime
from pyramid import testing
from sqlalchemy import Column
from sqlalchemy.types import DateTime
from pluserable.tests.models import Base
from . import IntegrationTestBase


class TestModel(Base):

    start_date = Column(DateTime)


class TestModels(IntegrationTestBase):

    def test_json(self):
        model = TestModel()
        model.id = 1
        model.start_date = datetime.now()

        data = {'id': 1, 'start_date': model.start_date.isoformat()}
        assert model.__json__(testing.DummyRequest()) == data


class TestUser(IntegrationTestBase):

    def test_password_hashing(self):
        """Passwords are not stored; only their hashes are stored."""
        from pluserable.tests.models import User
        user1 = self.create_users(count=1)
        self.sas.flush()

        assert user1.password != 'password'
        assert user1.salt is not None
