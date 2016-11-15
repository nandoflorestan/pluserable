"""Tests for the SQLAlchemy repository."""

from pluserable.db.sqlalchemy import Repository
from pluserable.tests.models import User, Group
from . import IntegrationTestBase


class TestRepository(IntegrationTestBase):
    """Tests for the SQLAlchemy repository."""

    def test_q_groups(self):
        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'
        self.session.add(user)

        group = Group(name='admin', description='group for admins')
        group.users.append(user)
        self.session.add(group)
        self.session.commit()

        repo = Repository(self.config.registry)
        groups = list(repo.q_groups())

        assert len(groups) == 1
