from . import IntegrationTestBase


class TestUser(IntegrationTestBase):

    def test_password_hashing(self):
        """Passwords are not stored; only their hashes are stored."""
        user1 = self.create_users(count=1)
        self.sas.flush()

        assert user1.password != 'password'
        assert user1.salt is not None
