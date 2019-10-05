"""Strings for easy internationalization."""

from pyramid.i18n import TranslationStringFactory
from pluserable import const
from kerno.web.pyramid import IKerno

_ = TranslationStringFactory("pluserable")


def get_strings(reg):
    """Return the configured Strings class."""
    if hasattr(reg, "getUtility"):  # reg must be a Zope/Pyramid registry
        reg = reg.getUtility(IKerno)  # otherwise reg gotta be the Kerno:
    return reg.utilities[const.STRING_CLASS]


class UIStringsBase:
    """A class containing all GUI strings in the application.

    User apps can simply subclass and change whatever text they want.
    """

    activation_check_email = _(
        "Thank you for registering! Please check your e-mail now. You can "
        "continue by clicking the activation link we have sent you."
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

    wrong_email = _("Wrong email or password.")
    wrong_username = _("Wrong username or password.")
    inactive_account = _(
        "Your account is not active; please check your e-mail."
    )

    edit_profile_email_present = _(
        "That email address ({email}) belongs to another user."
    )
    edit_profile_done = _("Your profile has been updated.")

    registration_email_exists = _(
        "Sorry, an account with the email {} "
        "already exists. Try logging in instead."
    )
    registration_username_exists = _(
        "Sorry, an account with this username already exists. "
        "Please enter another one."
    )
    registration_done = _("You have been registered. You may log in now!")

    reset_password_done = _("Your password has been reset!")
    reset_password_email_must_exist = _(
        'We have no user with the email "{}". '
        "Try correcting this address or trying another."
    )
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
        "Please check your e-mail to finish resetting your password."
    )
    username_may_not_contain_at = _("May not contain this character: @")
    user_not_found_title = _("User not found")
    user_not_found = _("That user cannot be found in the system.")
    unacceptable_characters = _("Contains unacceptable characters.")
