"""Use ZODB to retrieve and store models."""

import ZODB
from bag.reify import reify
from pluserable import const

# TODO: How is a unique "column" enforced in ZODB?


class Repository:
    """This repository is incomplete work. TODO: FINISH IT."""

    db = ZODB.DB(None)  # Create an in-memory database, just testing for now
    # TODO: Replace all SQLAlchemy stuff ("self.sas")

    def __init__(self, kerno, session_factory):
        """Constructor."""
        self.kerno = kerno
        self.con = self.db.open()
        if 'users' not in self.root:
            self.root['users'] = []  # TODO: Use the persistent collections

    @reify
    def User(self):
        return self.kerno.utilities[const.USER_CLASS]

    @reify
    def Activation(self):
        return self.kerno.utilities[const.ACTIVATION_CLASS]

    @reify
    def Group(self):
        return self.kerno.utilities[const.GROUP_CLASS]

    @reify
    def root(self):
        return self.con.root()

    def flush(self):
        pass

    def q_user_by_activation(self, activation):
        """Return the Activation with ``activation``, or None."""
        return self.sas.query(self.User).filter(
            self.User.activation_id == activation.id).first()

    def q_user_by_id(self, id):
        """Return a user with ``id``, or None."""
        # print("\nFetching {} #{}\n".format(self.User, id))
        return self.sas.query(self.User).get(id)

    def get_user_by_email(self, email):
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
        return self.root['users']

    def store_user(self, user):
        """Save the ``user`` instance."""
        self.root['users'].append(user)

    def q_groups(self):
        """Return an iterator on all groups."""
        return self.root['groups']

    def q_group_by_id(self, id):
        """Return a group with ``id``, or None."""
        return self.sas.query(self.Group).get(id)

    def q_activations(self):
        """Return an iterator on all activations."""
        return self.root['activations']

    def store_activation(self, activation):
        """Save the ``activation`` instance."""
        self.root['activations'].append(activation)

    def q_activation_by_code(self, code):
        """Return the Activation with ``code``, or None."""
        return self.sas.query(self.Activation).filter(
            self.Activation.code == code).first()

    def delete_activation(self, user, activation):
        """Delete the Activation instance from the database."""
        assert isinstance(activation, self.Activation)
        user.activation = None
        self.sas.delete(activation)
