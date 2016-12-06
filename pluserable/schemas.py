"""Colander and Deform schemas."""

import re
import colander as c
import deform.widget as w
from .strings import get_strings, _


def email_exists(node, val):
    """Colander validator that ensures a User exists with the email."""
    request = node.bindings['request']
    user = request.replusitory.q_user_by_email(val)
    if not user:
        raise c.Invalid(node, get_strings(
            request.registry).reset_password_email_must_exist.format(val))


def unique_email(node, val):
    """Colander validator that ensures the email does not exist."""
    request = node.bindings['request']
    other = request.replusitory.q_user_by_email(val)
    if other:
        raise c.Invalid(node, get_strings(
            request.registry).registration_email_exists.format(other.email))


def unique_username(node, val):
    """Colander validator that ensures the username does not exist."""
    request = node.bindings['request']
    user = request.replusitory.q_user_by_username(val)
    if user is not None:
        raise c.Invalid(node, get_strings(
            request.registry).registration_username_exists)


def unix_username(node, value):
    """Colander validator that ensures the username is alphanumeric."""
    request = node.bindings['request']
    if not ALPHANUM.match(value):
        raise c.Invalid(node, get_strings(
            request.registry).unacceptable_characters)


ALPHANUM = re.compile(r'^[a-zA-Z0-9_.-]+$')


def username_does_not_contain_at(node, value):
    """Ensure the username does not contain an ``@`` character.

    This is important because the system can be configured to accept
    an email or a username in the same field at login time, so the
    presence or absence of the @ tells us whether it is an email address.

    This Colander validator is not being used by default. We are using the
    ``unix_username`` validator which does more. But we are keeping this
    validator here in case someone wishes to use it instead of
    ``unix_username``.
    """
    request = node.bindings['request']
    if '@' in value:
        raise c.Invalid(node, get_strings(
            request.registry).username_may_not_contain_at)


# Schema fragments
# ----------------
# These functions reduce duplication in the schemas defined below,
# while ensuring some constant values are consistent among those schemas.


def get_username_creation_node(
        title=_('User name'), description=_("Name with which you will log in"),
        validator=None):
    return c.SchemaNode(
        c.String(), title=title, description=description,
        validator=validator or c.All(
            c.Length(max=30), unix_username, unique_username))


def get_email_node(validator=None, description=None):
    return c.SchemaNode(
        c.String(), title=_('Email'), description=description,
        validator=validator or c.All(c.Email(), unique_email),
        widget=w.TextInputWidget(size=40, maxlength=260, type='email',
                                 placeholder=_("joe@example.com")))


def get_checked_password_node(description=_(
        "Your password must be harder than a dictionary word or proper name!"),
        **kw):
    return c.SchemaNode(
        c.String(), title=_('Password'), validator=c.Length(min=4),
        widget=w.CheckedPasswordWidget(),
        description=description, **kw)


# Schemas
# -------

class UsernameLoginSchema(c.Schema):

    handle = c.SchemaNode(c.String(), title=_('User name'))
    password = c.SchemaNode(c.String(), widget=w.PasswordWidget())


class EmailLoginSchema(c.Schema):
    """For login, some apps just use email and have no username column."""

    handle = get_email_node(validator=c.Email())
    password = c.SchemaNode(c.String(), widget=w.PasswordWidget())


class UsernameRegisterSchema(c.Schema):

    username = get_username_creation_node()
    email = get_email_node()
    password = get_checked_password_node()


class EmailRegisterSchema(c.Schema):

    email = get_email_node()
    password = get_checked_password_node()


class ForgotPasswordSchema(c.Schema):

    email = get_email_node(
        validator=c.All(c.Email(), email_exists),
        description=_("The email address under which you have your account."))


class UsernameResetPasswordSchema(c.Schema):

    username = c.SchemaNode(
        c.String(), title=_('User name'), missing=c.null,
        widget=w.TextInputWidget(template='readonly/textinput'))
    password = get_checked_password_node()


class EmailResetPasswordSchema(c.Schema):

    email = c.SchemaNode(
        c.String(), title=_('Email'), missing=c.null,
        widget=w.TextInputWidget(template='readonly/textinput'))
    password = get_checked_password_node()


class UsernameProfileSchema(c.Schema):

    username = c.SchemaNode(
        c.String(),
        widget=w.TextInputWidget(template='readonly/textinput'),
        missing=c.null)
    email = get_email_node(description=None, validator=c.Email())
    password = get_checked_password_node(missing=c.null)


class EmailProfileSchema(c.Schema):

    email = get_email_node(description=None, validator=c.Email())
    password = get_checked_password_node(missing=c.null)
