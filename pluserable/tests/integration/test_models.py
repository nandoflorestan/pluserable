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


class TestActivation(IntegrationTestBase):

    def test_create_activation_with_valid_until(self):
        from pluserable.tests.models import Activation

        dt = datetime.utcnow()
        activation1 = Activation()
        activation1.valid_until = dt
        assert activation1.valid_until == dt


class TestUser(IntegrationTestBase):

    def test_password_hashing(self):
        from pluserable.tests.models import User
        user1 = User(username='sagan', email='carlsagan@nasa.org')
        user1.password = 'password'
        self.sas.add(user1)
        self.sas.flush()

        assert user1.password != 'password'
        assert user1.salt is not None


class TestGroup(IntegrationTestBase):

    def test_init(self):
        from pluserable.tests.models import Group
        group = Group(name='foo', description='bar')

        assert group.name == 'foo'
        assert group.description == 'bar'

    def test_get_by_id(self):
        from pluserable.tests.models import Group
        from pluserable.tests.models import User

        group = Group(name='admin', description='group for admins')
        group2 = Group(name='employees', description='group for employees')

        self.sas.add(group)
        self.sas.add(group2)

        self.sas.commit()

        request = testing.DummyRequest()

        group = Group.get_by_id(request, group2.id)

        assert group.name == 'employees'
