"""Use the SQLAlchemy session to retrieve and store models."""

from pyramid.decorator import reify
from sqlalchemy import func
from pluserable import const
from pluserable.interfaces import IUserClass, IGroupClass


class Repository(object):
    """This repository uses SQLAlchemy for storage.

    In the future other strategies can be developed (e. g. ZODB).
    """

    def __init__(self, mundi):
        """Construct a SQLAlchemy repository for pluserable."""
        self.mundi = mundi
        # The SQLAlchemy session to be used in this request:
        self.sas = mundi.get_utility(const.SAS)

    @reify
    def User(self):
        return self.mundi.get_utility(const.USERCLASS)

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
