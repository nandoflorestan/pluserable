"""Strings for easy internationalization."""

from pluserable import const
from pluserable.interfaces import IMundi
from pluserable.models import _


def get_strings(reg):
    """Return the configured Strings class."""
    if hasattr(reg, 'getUtility'):  # reg must be a Zope/Pyramid registry
        reg = reg.getUtility(IMundi)  # otherwise reg gotta be the Mundi:
    return reg.get_utility(const.STRING_CLASS)


class UIStringsBase(object):
    """A class containing all GUI strings in the application.

    User apps can simply subclass and change whatever text they want.
    """

    activation_check_email = \
        _("Thank you for registering! Please check your e-mail now. You can "
          "continue by clicking the activation link we have sent you.")
    activation_email_verified = _("Your e-mail address has been verified. "
                                  "Thank you!")

    authenticated = _('You are now logged in.')
    login_button = _('Log in')
    logout = _('You have logged out.')

    wrong_email = _('Wrong email or password.')
    wrong_username = _('Wrong username or password.')
    inactive_account = _(
        'Your account is not active; please check your e-mail.')

    edit_profile_email_present = _(
        'That email address ({email}) belongs to another user.')
    edit_profile_done = _('Your profile has been updated.')

    registration_email_exists = _("Sorry, an account with the email {} "
                                  "already exists. Try logging in instead.")
    registration_username_exists = _(
        "Sorry, an account with this username already exists. "
        "Please enter another one.")
    registration_done = _('You have been registered. You may log in now!')

    reset_password_done = _('Your password has been reset!')
    reset_password_email_must_exist = _(
        'We have no user with the email "{}". '
        'Try correcting this address or trying another.')
    reset_password_email_body = _("""\
Hello, {username}!

Someone requested resetting your password. If it was you, click here:
{link}

If you don't want to change your password, please ignore this email message.

Regards,
{domain}\n""")
    reset_password_email_subject = _("Reset your password")
    # You don't want to say "E-mail not registered" or anything like that
    # because it gives spammers context:
    reset_password_email_sent = _("Please check your e-mail to finish "
                                  "resetting your password.")
    username_may_not_contain_at = _("May not contain this character: @")
