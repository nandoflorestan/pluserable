"""Use the SQLAlchemy session to retrieve and store models."""

from pyramid.decorator import reify
from sqlalchemy import func
from pluserable.interfaces import IDBSession, IUserClass, IGroupClass


class Repository(object):
    """This repository uses SQLAlchemy for storage.

    In the future other strategies can be developed (e. g. ZODB).
    """

    def __init__(self, registry):
        self.registry = registry

    @reify
    def sas(self):
        """The SQLAlchemy session to be used in this request."""
        session = self.registry.getUtility(IDBSession)
        if session is None:
            raise RuntimeError(
                'You must let pluserable know what SQLAlchemy session to use.')
        return session

    @reify
    def User(self):
        return self.registry.getUtility(IUserClass)

    @reify
    def Group(self):
        return self.registry.getUtility(IGroupClass)

    def q_user_by_email(self, email):
        """Return a user with ``email``, or None."""
        return self.sas.query(self.User).filter(
            self.User.email.ilike(email)).first()

    def q_user_by_username(self, username):
        """Return a user with ``username``, or None. Case-insensitive."""
        return self.sas.query(self.User).filter(
            # self.User.username == username
            func.lower(self.User.username) == username.lower()
        ).first()

    def q_groups(self):
        """Return an iterator on all groups."""
        return self.sas.query(self.Group)
