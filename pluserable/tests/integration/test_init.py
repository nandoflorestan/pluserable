from pyramid import testing
from mock import Mock
from pluserable.resources import RootFactory
from pyramid.security import Authenticated, Allow, ALL_PERMISSIONS
from pluserable import groupfinder
from pluserable.tests.models import User, Group
from . import IntegrationTestBase


class TestInitCase(IntegrationTestBase):

    '''def test_request_factory(self):
       from pluserable import SignUpRequestFactory
       from pluserable.tests.models import User

       user1 = User(username='sagan', email='carlsagan@nasa.org')
       user1.password = 'foo'
       self.sas.add(user1)
       self.sas.flush()

       with patch('pluserable.unauthenticated_userid') as unauth:
           unauth.return_value = 1
           request = SignUpRequestFactory({})
           request.registry = Mock()

           getUtility = Mock()
           getUtility.return_value = self.sas

           request.registry.getUtility = getUtility

           user = request.user

           assert user == user1'''

    def test_group_finder(self):
        group = Group(name='foo', description='bar')
        user1 = User(username='sagan', email='carlsagan@nasa.org')
        user1.password = 'foo'
        group.users.append(user1)

        self.sas.add(group)
        self.sas.add(user1)
        self.sas.flush()

        request = Mock()
        request.user = user1

        results = groupfinder(1, request)

        assert 'group:foo' in results
        assert 'user:%s' % (user1.id) in results
        assert len(results) == 2

    def test_group_finder_no_groups(self):
        group = Group(name='foo', description='bar')
        user1 = User(username='sagan', email='carlsagan@nasa.org')
        user2 = User(username='sagan2', email='carlsagan2@nasa.org')
        user1.password = 'foo'
        user2.password = 'foo'
        group.users.append(user1)

        self.sas.add(group)
        self.sas.add(user1)
        self.sas.add(user2)
        self.sas.flush()

        request = Mock()
        request.user = user2

        results = groupfinder(2, request)

        assert len(results) == 1
        assert 'user:%s' % (user2.id) in results
