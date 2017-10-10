"""Interfaces for the user app to register utilities for pluserable."""

from zope.interface import Interface


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
