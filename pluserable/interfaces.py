"""Interfaces for the user app to register utilities for pluserable."""

from zope.interface import Interface


class IDBSession(Interface):
    """Marker interface for registering a SQLAlchemy session."""


class IUIStrings(Interface):
    """Marker interface for a class containing translation strings."""


class IMundi(Interface):
    """Marker interface for registering our Mundi instance."""


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
