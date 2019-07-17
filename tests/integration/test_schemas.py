"""Tests for our schemas."""

from colander import Invalid
from pluserable.schemas import UsernameLoginSchema, UsernameRegisterSchema

from tests.integration import IntegrationTestBase


class TestSchemas(IntegrationTestBase):  # noqa

    def test_valid_login_schema(self):  # noqa
        request = self.get_request(post={
            'handle': 'sagan',
            'password': 'password',
            'csrf_token': 'irrelevant but required',
        })
        schema = UsernameLoginSchema().bind(request=request)

        result = schema.deserialize(request.POST)

        assert result['handle'] == 'sagan'
        assert result['password'] == 'password'

    def test_invalid_login_schema(self):  # noqa
        request = self.get_request()
        schema = UsernameLoginSchema().bind(request=request)

        def deserialize_empty():
            try:
                schema.deserialize({})
            except Invalid as exc:
                assert len(exc.children) == 3
                errors = ['handle', 'password', 'csrf_token']
                for child in exc.children:
                    assert child.node.name in errors
                    assert child.msg == 'Required'
                raise
        self.assertRaises(Invalid, deserialize_empty)

    def test_usernames_may_not_contain_at(self):  # noqa
        POST = {
            'username': 'bru@haha',
            'email': 'sagan@nasa.gov',
            'password': 'pass',
            'csrf_token': 'irrelevant but required',
        }
        request = self.get_request(post=POST)
        schema = UsernameRegisterSchema().bind(request=request)

        def run():
            try:
                schema.deserialize(POST)
            except Invalid as exc:
                assert len(exc.children) == 1
                the_error = exc.children[0]
                assert the_error.node.name == 'username'
                assert the_error.msg == ['Contains unacceptable characters.']
                raise
        self.assertRaises(Invalid, run)

    def test_usernames_may_contain_dot_dash_underline(self):  # noqa
        handle = 'Sagan-was-a-GREAT_writer.'
        POST = {
            'username': handle,
            'email': 'sagan@nasa.gov',
            'password': 'pass',
            'csrf_token': 'irrelevant but required',
        }
        request = self.get_request(post=POST)
        schema = UsernameRegisterSchema().bind(request=request)

        result = schema.deserialize(request.POST)
        assert result['username'] == handle
        assert result['password'] == 'pass'
        assert result['email'] == 'sagan@nasa.gov'
