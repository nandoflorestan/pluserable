"""Use the SQLAlchemy session to retrieve and store models."""

from mundi.repository.sqlalchemy import BaseSQLAlchemyRepository
from pyramid.decorator import reify
from sqlalchemy import func
from pluserable import const
from pluserable.interfaces import IGroupClass


class Repository(BaseSQLAlchemyRepository):
    """This repository uses SQLAlchemy for storage.

    In the future other strategies can be developed (e. g. ZODB).
    """

    @reify
    def User(self):
        return self.mundi.get_utility(const.USER_CLASS)

    @reify
    def Activation(self):
        return self.mundi.get_utility(const.ACTIVATION_CLASS)

    @reify
    def Group(self):
        return self.mundi.get_utility(const.GROUP_CLASS)

    def q_user_by_id(self, id):
        """Return a user with ``id``, or None."""
        return self.sas.query(self.User).get(id)

    def q_user_by_email(self, email):
        """Return a user with ``email``, or None."""
        return self.sas.query(self.User).filter(
            self.User.email.ilike(email)).first()

    def q_user_by_username(self, username):
        """Return a user with ``username``, or None. Case-insensitive."""
        return self.sas.query(self.User).filter(
            # self.User.username == username
            func.lower(self.User.username) == username.lower()).first()

    def q_users(self):
        """Return an iterator on all users."""
        return self.sas.query(self.User)

    def q_groups(self):
        """Return an iterator on all groups."""
        return self.sas.query(self.Group)

    def q_activation_by_code(self, code):
        """Return the Activation with ``code``, or None."""
        return self.sas.query(self.Activation).filter(
            self.Activation.code == code).first()

    def q_user_by_activation(self, activation):
        """Return the Activation with ``activation``, or None."""
        return self.sas.query(self.User).filter(
            self.User.activation_id == activation.id_value).first()
