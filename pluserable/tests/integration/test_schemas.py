"""Tests for our schemas."""

from colander import Invalid
from pluserable.schemas import UsernameLoginSchema, UsernameRegisterSchema
from . import IntegrationTestBase


class TestSchemas(IntegrationTestBase):
    def test_valid_login_schema(self):
        request = self.get_request(post={
            'handle': 'sagan',
            'password': 'password',
        })
        schema = UsernameLoginSchema().bind(request=request)

        result = schema.deserialize(request.POST)

        assert result['handle'] == 'sagan'
        assert result['password'] == 'password'

    def test_invalid_login_schema(self):
        request = self.get_request()
        schema = UsernameLoginSchema().bind(request=request)

        def deserialize_empty():
            try:
                schema.deserialize({})
            except Invalid as exc:
                assert len(exc.children) == 2
                errors = ['handle', 'password']
                for child in exc.children:
                    assert child.node.name in errors
                    assert child.msg == 'Required'
                raise
        self.assertRaises(Invalid, deserialize_empty)

    def test_usernames_may_not_contain_at(self):
        POST = dict(username='bru@haha', email='bru@haha.com', password='pass')
        request = self.get_request(post=POST)
        schema = UsernameRegisterSchema().bind(request=request)

        def run():
            try:
                schema.deserialize(POST)
            except Invalid as exc:
                assert len(exc.children) == 1
                the_error = exc.children[0]
                assert the_error.node.name == 'username'
                assert the_error.msg == ['May not contain this character: @']
                raise
        self.assertRaises(Invalid, run)
