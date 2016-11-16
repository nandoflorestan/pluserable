"""Interfaces for the user app to register utilities for pluserable."""

from zope.interface import Interface


class IDBSession(Interface):
    """Marker interface for registering a SQLAlchemy session."""


class IUIStrings(Interface):
    """Marker interface for a class containing translation strings."""


class IRepositoryClass(Interface):
    """Marker interface for registering a Repository class."""


class IUserClass(Interface):
    """Interface for a user model class."""


class IGroupClass(Interface):
    """Interface for a group model class."""


class IActivationClass(Interface):
    """Interface for a user activation model class."""


class ILoginSchema(Interface):
    pass


class ILoginForm(Interface):
    pass


class IRegisterSchema(Interface):
    pass


class IRegisterForm(Interface):
    pass


class IForgotPasswordForm(Interface):
    pass


class IForgotPasswordSchema(Interface):
    pass


class IResetPasswordForm(Interface):
    pass


class IResetPasswordSchema(Interface):
    pass


class IProfileForm(Interface):
    pass


class IProfileSchema(Interface):
    pass
