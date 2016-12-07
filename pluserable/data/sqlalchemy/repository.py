"""Use the SQLAlchemy session to retrieve and store models."""

from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
from pyramid.decorator import reify
from sqlalchemy import func
from pluserable import const


class Repository(BaseSQLAlchemyRepository):
    """This repository uses SQLAlchemy for storage.

    In the future other strategies can be developed (e. g. ZODB).
    """

    @reify
    def User(self):
        return self.kerno.get_utility(const.USER_CLASS)

    @reify
    def Activation(self):
        return self.kerno.get_utility(const.ACTIVATION_CLASS)

    @reify
    def Group(self):
        return self.kerno.get_utility(const.GROUP_CLASS)

    def q_user_by_activation(self, activation):
        """Return the Activation with ``activation``, or None."""
        return self.sas.query(self.User).filter(
            self.User.activation_id == activation.id).first()

    def q_user_by_id(self, id):
        """Return a user with ``id``, or None."""
        # print("\nFetching {} #{}\n".format(self.User, id))
        return self.sas.query(self.User).get(id)

    def q_user_by_email(self, email):
        """Return a user with ``email``, or None."""
        return self.sas.query(self.User).filter(
            func.lower(self.User.email) == email.lower()).first()

    def q_user_by_username(self, username):
        """Return a user with ``username``, or None. Case-insensitive."""
        return self.sas.query(self.User).filter(
            # self.User.username == username
            func.lower(self.User.username) == username.lower()).first()

    def q_users(self):
        """Return an iterator on all users."""
        return self.sas.query(self.User)

    def store_user(self, user):
        """Save the ``user`` instance."""
        self.sas.add(user)

    def q_groups(self):
        """Return an iterator on all groups."""
        return self.sas.query(self.Group)

    def q_group_by_id(self, id):
        """Return a group with ``id``, or None."""
        return self.sas.query(self.Group).get(id)

    def q_activations(self):
        """Return an iterator on all activations."""
        return self.sas.query(self.Activation)

    def store_activation(self, activation):
        """Save the ``activation`` instance."""
        self.sas.add(activation)

    def q_activation_by_code(self, code):
        """Return the Activation with ``code``, or None."""
        return self.sas.query(self.Activation).filter(
            self.Activation.code == code).first()

    def delete_activation(self, user, activation):
        """Delete the Activation instance from the database."""
        assert isinstance(activation, self.Activation)
        user.activation = None
        self.sas.delete(activation)
