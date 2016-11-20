"""Tests for the SQLAlchemy repository."""

from pluserable.repository import instantiate_repository
from pluserable.tests.models import Activation, Group
from . import IntegrationTestBase


class TestRepository(IntegrationTestBase):
    """Tests for the SQLAlchemy repository."""

    def test_q_groups(self):
        """q_groups() returns all groups."""
        user = self.create_users(count=1)
        group = Group(name='admin', description='group for admins')
        group.users.append(user)
        self.session.flush()

        repo = instantiate_repository(self.config.registry)
        groups = list(repo.q_groups())
        assert len(groups) == 1
        assert len(groups[0].users) == 1

    def test_q_activation_by_code(self):
        """q_activation_by_code() returns the correct activation."""
        activation = Activation()
        self.session.add(activation)
        self.session.flush()

        repo = instantiate_repository(self.config.registry)
        new_activation = repo.q_activation_by_code(activation.code)

        assert activation is new_activation

    def test_q_activation_by_code_leads_to_user(self):
        """q_activation_by_code() leads to the correct user."""
        user1, user2 = self.create_users(count=2)
        activation = Activation()
        user2.activation = activation
        self.session.flush()

        repo = instantiate_repository(self.config.registry)
        new_user = repo.q_user_by_username('sagan2')
        new_activation = repo.q_activation_by_code(activation.code)

        assert activation is new_activation
        assert new_user.activation is new_activation

    def test_gen_users(self):
        """q_users() returns all existing users."""
        self.create_users(count=2)
        self.session.flush()

        repo = instantiate_repository(self.config.registry)
        users = list(repo.q_users())
        assert len(users) == 2

    def test_q_user_by_email(self):
        """q_user_by_email() called with valid email returns the user."""
        user = self.create_users(count=1)
        self.session.flush()

        repo = instantiate_repository(self.config.registry)
        new_user = repo.q_user_by_email(user.email)

        assert new_user is user

    def test_q_user_by_invalid_email(self):
        """q_user_by_email() called with invalid email returns None."""
        self.create_users(count=1)
        self.session.flush()

        repo = instantiate_repository(self.config.registry)
        new_user = repo.q_user_by_email('someone@else.com')

        assert new_user is None
