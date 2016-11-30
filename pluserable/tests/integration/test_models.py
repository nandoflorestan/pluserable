from datetime import datetime
from pyramid import testing
from sqlalchemy import Column
from sqlalchemy.types import DateTime
from pluserable.tests.models import Base
from . import IntegrationTestBase


class TestModel(Base):

    start_date = Column(DateTime)


class TestModels(IntegrationTestBase):

    def test_tablename(self):
        model = TestModel()
        assert model.__tablename__ == 'test_model'

    def test_json(self):
        model = TestModel()
        model.id = 1
        model.start_date = datetime.now()

        data = {'id': 1, 'start_date': model.start_date.isoformat()}
        assert model.__json__(testing.DummyRequest()) == data


class TestUser(IntegrationTestBase):

    def test_password_hashing(self):
        from pluserable.tests.models import User
        user1 = User(username='sagan', email='carlsagan@nasa.org')
        user1.password = 'password'
        self.sas.add(user1)
        self.sas.flush()

        assert user1.password != 'password'
        assert user1.salt is not None
