"""Tests for the SQLAlchemy repository."""

from tests.models import Activation, Group
from tests.integration import IntegrationTestBase


class TestRepository(IntegrationTestBase):
    """Tests for the SQLAlchemy repository."""

    def test_q_groups(self):
        """q_groups() returns all groups."""
        user = self.create_users(count=1)
        group = Group(name="admin", description="group for admins")
        group.users.append(user)
        self.sas.flush()

        groups = list(self.repo.q_groups())
        assert len(groups) == 1
        assert len(groups[0].users) == 1

    def test_get_activation_by_code(self):
        """get_activation_by_code() returns the correct activation."""
        activation = Activation()
        self.sas.add(activation)
        self.sas.flush()

        new_activation = self.repo.get_activation_by_code(activation.code)

        assert activation is new_activation

    def test_get_activation_by_code_leads_to_user(self):
        """get_activation_by_code() leads to the correct user."""
        user1, user2 = self.create_users(count=2)
        activation = Activation()
        user2.activation = activation
        self.sas.flush()

        new_user = self.repo.get_user_by_username("sagan2")
        new_activation = self.repo.get_activation_by_code(activation.code)

        assert activation is new_activation
        assert new_user.activation is new_activation

    def test_get_user_by_id(self):
        """get_user_by_id() called with valid id returns the user."""
        users = self.create_users(count=2)
        self.sas.flush()

        ret = self.repo.get_user_by_id(users[1].id)
        assert ret is users[1]

    def test_get_user_by_id_invalid(self):
        """get_user_by_id() called with invalid id returns None."""
        self.create_users(count=1)
        self.sas.flush()

        ret = self.repo.get_user_by_id(2)
        assert ret is None

    def test_get_user_by_email(self):
        """get_user_by_email() called with valid email returns the user."""
        user = self.create_users(count=1)
        self.sas.flush()

        ret = self.repo.get_user_by_email(user.email)
        assert ret is user

    def test_get_user_by_email_invalid(self):
        """get_user_by_email() called with invalid email returns None."""
        self.create_users(count=1)
        self.sas.flush()

        new_user = self.repo.get_user_by_email("someone@else.com")

        assert new_user is None

    def test_get_user_by_username(self):
        """get_user_by_username() returns the user."""
        user = self.create_users(count=1)
        self.sas.flush()

        ret = self.repo.get_user_by_username(user.username)
        assert ret is user

    def test_get_user_by_username_invalid(self):
        """get_user_by_username(), with invalid username, returns None."""
        self.create_users(count=1)
        self.sas.flush()

        ret = self.repo.get_user_by_username("wrong")
        assert ret is None

    def test_get_user_by_activation(self):
        """get_user_by_activation() returns the correct user."""
        users = self.create_users(count=2)
        activation = Activation()
        users[1].activation = activation
        self.sas.flush()

        ret = self.repo.get_user_by_activation(activation)
        assert ret is users[1]
