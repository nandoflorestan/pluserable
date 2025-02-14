"""Strings for easy internationalization."""

from __future__ import annotations  # allows forward references; python 3.7+
from typing import TYPE_CHECKING

from pyramid.i18n import TranslationStringFactory
from kerno.web.pyramid import IKerno

from pluserable import const

if TYPE_CHECKING:
    from kerno.kerno import Kerno
    from pyramid.registry import Registry
    from pluserable.web.pyramid.typing import UserlessPeto

_ = TranslationStringFactory("pluserable")


def get_strings(reg: UserlessPeto | Kerno | Registry):
    """Return the configured Strings class."""
    if hasattr(reg, "kerno"):  # reg might be a Peto
        kerno = reg.kerno
    elif hasattr(reg, "getUtility"):  # reg must be a Zope/Pyramid registry
        kerno = reg.getUtility(IKerno)
    # Check for "utilities" must come AFTER check for "getUtility"!
    elif hasattr(reg, "utilities"):  # reg must be a Kerno instance
        kerno = reg
    else:
        raise TypeError(f"reg cannot be a {type(reg)}.")
    return kerno.utilities[const.STRING_CLASS]


class UIStringsBase:
    """A class containing all GUI strings in the application.

    User apps can simply subclass and change whatever text they want.
    """

    activation_check_email = _(
        "Thank you for registering! Please check your e-mail now. You can "
        "continue by clicking the activation link we have sent you. "
        "If you do not receive an e-mail in the next 5 minutes "
        "please check your spam folder!"
    )
    activation_code_not_found_title = _("Activation code not found")
    activation_code_not_found = _(
        "That activation code cannot be found in the system. Maybe you "
        "already used it -- in this case, just try logging in. If you cannot, "
        '(from the login page) click on "Forgot password" to set a password '
        "and activate your user."
    )
    activation_code_not_match_title = _("Code and user do not match")
    activation_code_not_match = _("That code does not belong to that user.")
    activation_email_subject = _("Please activate your account!")
    activation_email_plain = _(
        "Please validate your email and activate your account by visiting:\n"
        "ACTIVATION_LINK\n\nThe above link is only valid for one use, so "
        "after this process you can delete this email message."
    )
    activation_email_verified_title = _("E-mail verified!")
    activation_email_verified = _(
        "Your e-mail address has been verified. " "Thank you!"
    )

    login_button = _("Log in")
    login_done = _("You are now logged in.")
    logout_done = _("You have logged out.")
    login_is_blocked = _(
        "Your login attempt was ignored. You must wait {seconds} seconds "
        "(until {until}) before retrying. "
        "This wait helps prevent brute force attacks on your password. "
        "The waiting time is exponentially increased each time. "
        "If you don't remember your password, it's best to reset it."
    )
    registration_blocked_title = _(
        "You are temporarily blocked from registering again."
    )
    registration_is_blocked = _(
        "Your registration attempt was ignored. You must wait {seconds} seconds "
        "(until {until}) before retrying. This wait helps prevent "
        "brute force attacks. The number of registrations per day is severely "
        "limited. If you don't know whether you already have an account, "
        "it is best to try resetting your password."
    )

    wrong_email = _(
        "Wrong email or password. You must wait {seconds} seconds before retrying."
    )
    wrong_username = _(
        "Wrong username or password. You must wait {seconds} seconds before retrying."
    )
    inactive_account = _("Your account is not active; please check your e-mail.")

    edit_profile_email_present = _(
        "That email address ({email}) belongs to another user."
    )
    edit_profile_done = _("Your profile has been updated.")

    email_domain_blocked = _("The domain {} is not acceptable.")

    registration_username_exists = _(
        "Sorry, an account with this username already exists. "
        "Please enter another one."
    )
    registration_done = _("You have been registered. You may log in now!")

    reset_password_done = _("Your password has been reset!")
    reset_password_email_body = _(
        """\
Hello, {username}!

Someone requested resetting your password. If it was you, click here:
{link}

If you don't want to change your password, please ignore this email message.

Regards,
{domain}\n"""
    )
    reset_password_email_subject = _("Reset your password")
    # You don't want to say "E-mail not registered" or anything like that
    # because it gives spammers context:
    reset_password_email_sent = _(
        "If you have an account with us, you are receiving an email message. "
        "Please check your email to finish resetting your password."
    )
    username_may_not_contain_at = _("May not contain this character: @")
    user_not_found_title = _("User not found")
    user_not_found = _("That user cannot be found in the system.")
    unacceptable_characters = _("Contains unacceptable characters.")
