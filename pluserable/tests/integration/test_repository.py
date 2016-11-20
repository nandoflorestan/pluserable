"""Tests for the SQLAlchemy repository."""

from pluserable.repository import instantiate_repository
from pluserable.tests.models import Activation, User, Group
from . import IntegrationTestBase


class TestRepository(IntegrationTestBase):
    """Tests for the SQLAlchemy repository."""

    def test_q_groups(self):
        user = User(username='sagan', email='sagan@gmail.com')
        user.password = 'temp'
        self.session.add(user)

        group = Group(name='admin', description='group for admins')
        group.users.append(user)
        self.session.add(group)
        self.session.commit()

        repo = instantiate_repository(self.config.registry)
        groups = list(repo.q_groups())

        assert len(groups) == 1

    def test_q_activation_by_code(self):
        activation = Activation()
        self.session.add(activation)
        self.session.commit()

        repo = instantiate_repository(self.config.registry)
        new_activation = repo.q_activation_by_code(activation.code)

        assert activation is new_activation

    def test_get_user_activation(self):
        user1 = User(username='sagan1', email='sagan@gmail.com')
        user2 = User(username='sagan2', email='sagan+2@gmail.com')
        user1.password = 'password'
        user2.password = 'password'

        activation = Activation()
        user2.activation = activation

        self.session.add(user1)
        self.session.add(user2)
        self.session.commit()

        repo = instantiate_repository(self.config.registry)
        new_user = repo.q_user_by_username('sagan2')
        new_activation = repo.q_activation_by_code(activation.code)

        assert activation is new_activation
        assert new_user.activation is new_activation
