"""Use the SQLAlchemy session to retrieve and store models."""

from pyramid.decorator import reify
from pluserable.interfaces import IDBSession, IUserClass


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

    def q_user_by_email(self, email):
        """Return a user with ``email``, or None."""
        return self.sas.query(self.User).filter(
            self.User.email.ilike(email)).first()

    def q_user_by_username(self, username):
        """Return a user with ``username``, or None."""
        return self.sas.query(self.User).filter(
            self.User.username == username).first()
