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
        self.session.add(user1)
        self.session.flush()

        assert user1.password != 'password'
        assert user1.salt is not None

    def test_get_valid_user(self):
        from pluserable.tests.models import User
        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        new_user = User.get_user(request, 'sagan', 'temp')
        assert user is new_user

    def test_get_valid_user_by_security_code(self):
        from pluserable.tests.models import User
        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        new_user = User.get_by_security_code(request, user.security_code)
        assert user is new_user

    def test_get_invalid_user(self):
        from pluserable.tests.models import User
        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        new_user = User.get_user(request, 'sagan', 'temp')
        assert new_user is None

    def test_get_user_by_id(self):
        from pluserable.tests.models import User
        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        new_user = User.get_by_id(request, user.id)
        assert new_user is user

    def test_get_user_by_invalid_id(self):
        from pluserable.tests.models import User
        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        new_user = User.get_by_id(request, 2)
        assert new_user is None

    def test_get_user_by_username(self):
        from pluserable.tests.models import User

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()

        new_user = User.get_by_username(request, 'sagan')

        assert new_user is user

    def test_get_user_by_invalid_username(self):
        from pluserable.tests.models import User

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()

        new_user = User.get_by_username(request, 'sagan')

        assert new_user is None

    def test_get_user_by_activation(self):
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'password'
        activation = Activation()
        user.activation = activation

        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        new_user = User.get_by_activation(request, activation)
        assert new_user is user

    def test_get_user_by_activation_with_multiple_users(self):
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation

        user1 = User(username='sagan', email='carlsagan@nasa.org')
        user2 = User(username='sagan2', email='carlsagan2@nasa.org')
        user1.password = 'password'
        user2.password = 'password2'
        activation = Activation()
        user2.activation = activation

        self.session.add(user1)
        self.session.add(user2)

        self.session.commit()

        request = testing.DummyRequest()

        new_user = User.get_by_activation(request, activation)

        assert new_user is user2


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

        self.session.add(group)
        self.session.add(group2)

        self.session.commit()

        request = testing.DummyRequest()

        group = Group.get_by_id(request, group2.id)

        assert group.name == 'employees'
