# noqa

from unittest.mock import Mock, patch
from tests.slow import FunctionalTestBase


class TestViews(FunctionalTestBase):  # noqa
    def test_index(self):
        """Call the index view; make sure routes are working."""
        res = self.app.get("/")
        assert res.status_int == 200

    def test_get_register(self):
        """Call the register view; make sure routes are working."""
        res = self.app.get("/register")
        assert res.status_int == 200

    def test_show_login(self):
        """Call the login view; make sure routes are working."""
        res = self.app.get("/login")
        self.assertEqual(res.status_int, 200)

    def test_empty_login_fails(self):  # noqa
        res = self.app.post("/login", {"submit": True})

        assert b"There was a problem with your submission" in res.body
        assert b"Required" in res.body
        assert res.status_int == 200

    def test_valid_login(self):
        """Call the login view, make sure routes are working."""
        user = self.create_users(count=1, password="science")
        self.sas.flush()

        res = self.app.get("/login")
        res = self.app.post(
            "/login",
            {
                "submit": True,
                "handle": user.username,
                "password": "science",
                "csrf_token": "irrelevant but required",
            },
        )
        assert res.status_int == 302

    def test_inactive_login(self):
        """Make sure inactive users can't sign in."""
        user = self.create_users(count=1, password="science", activation=True)
        self.sas.flush()

        res = self.app.get("/login")
        res = self.app.post(
            "/login",
            {
                "submit": True,
                "handle": user.username,
                "password": "science",
                "csrf_token": "irrelevant but required",
            },
        )
        assert (
            b"Your account is not active; please check your e-mail."
            in res.body
        )
