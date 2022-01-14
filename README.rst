============================
Introduction to *pluserable*
============================

*pluserable* provides generic user registration for the Pyramid
web framework, if your web app uses SQLAlchemy.

It is a pluggable web application that provides user registration, login,
logout and change password functionality. *pluserable* follows a policy of
minimal interference, so your app can mostly keep its existing models.

*pluserable* is highly configurable, you can make it do what you want.

It is gradually being refactored to support other web frameworks, too.

The documentation is at http://docs.nando.audio/pluserable/latest/


Minimal integration
===================

- Create a virtualenv and activate it. Install pyramid and create
  your Pyramid project.

- Ensure you have some SQLAlchemy declarative initialization.
  This is usually created by the Pyramid scaffold.

- Edit your *setup.py* to add "pluserable" to the dependencies in the
  *install_requires* list.

- Run ``python setup.py develop`` on your project to install all
  dependencies into your virtualenv.

- Create models inheriting from pluserable's abstract models.
  Find an example in the file `pluserable/tests/models.py
  <https://github.com/nandoflorestan/pluserable/blob/master/pluserable/tests/models.py>`_.

- In your Pyramid configuration file, create a section called
  "kerno utilities" like this::

    [kerno utilities]
        # Let pluserable know which model classes to use:
        activation class = some.app.models:Activation
        group class = some.app.models:Group
        user class = some.app.models:User

        # Give pluserable a SQLAlchemy session factory:
        session factory = some.app.models:get_sqlalchemy_session

- Above you are also pointing to a session factory. Just write a
  function that returns a SQLAlchemy session instance, ready for use.
  Alternatively, it can be a scoped session.

- Also add to your Pyramid configuration file a "pluserable" section
  like this::

    [pluserable]
        # Whether to log a user in directly after registration. Default: false.
        # autologin = false

        # Email domains we do not accept for registration. One per line.
        email_domains_blacklist =

        # Route or URL after a user confirms their email. Default: "index"
        # activate_redirect = index

        # Route or URL after a user fills the forgot password form. Default: "index"
        # forgot_password_redirect = index

        # Route or URL after a user logs in. Default: "index"
        # login_redirect = index

        # Route or URL after a user logs out. Default: "index"
        # logout_redirect = index

        # Route or URL after a user signs up for an account. Default: "index"
        # register_redirect = index

        # Route or URL after a user resets their password. Default: "index"
        # reset_password_redirect = index

        # Whether to enable retail rendering of deform forms. Default: false.
        # deform_retail = false

- pluserable includes a (very standard and vanilla) SecurityPolicy.
  If you wish to use it, do::

    config.include("pluserable.web.pyramid.security")

- You may write a function that returns a configuration for Pyramid routes and
  views (which is something you probably want to manipulate in code
  because it won't change between dev, staging and production environments),
  and then inform pluserable about it like this::

    registry.settings["pluserable_configurator"] = "my.package:some_function"

- Your ``pluserable_configurator`` function would look more or less like this::

    from pluserable.settings import get_default_pluserable_settings

    def my_pluserable(config):
        """This function is called by pluserable during app startup."""
        adict = get_default_pluserable_settings()
        # Manipulate adict to customize pluserable for your application, then
        return adict

- Include **pluserable** into your Pyramid application,
  just after Pyramid's Configurator is instantiated::

    from kerno.start import Eko

    def includeme(config):
        """Stuff called during Pyramid initialization."""
        eko = Eko.from_ini("server.ini")
        eko.include("pluserable")
        config.include("pluserable")

This does almost nothing: it only makes a new config method available.
You have to use it next::

    config.setup_pluserable(  # Directive that starts pluserable up
        global_settings["__file__"],  # Path to your INI configuration file
    )

The above causes **pluserable** to read your INI file -- especially
the ``[Kerno utilities]`` and ``[pluserable]`` sections.

The backend for database access is in a separate class, this way you can
substitute the implementation. This is called the "repository" pattern.
One of the main benefits is, it makes writing tests much easier.
It is recommended that you use the repository pattern in your app, too.
The pluserable repository is instantiated once per request. It is available
in the ``request.repo`` variable.

- If you haven't done so yet, configure an HTTP session factory according to
  the Sessions chapter of the Pyramid documentation.

- Create your database and tables. Maybe even an initial user.

- Be sure to pass an ``authentication_policy`` argument in the
  ``config = Configurator(...)`` call. Refer to Pyramid docs for details.

- By now the login form should appear at /login, but /register shouldn't.

- Include the package pyramid_mailer for the validation e-mail and
  "forgot password" e-mail::

    config.include("pyramid_mailer")

- The /register form should appear, though ugly. Now you have a choice
  regarding user activation by email:

  - You may just disable user activation by setting, in your .ini file::

      [pluserable]
          # (other settings, then...)
          require_activation = false

  - Otherwise, configure pyramid_mailer `according to its documentation
    <http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/>`_
    and test the registration page.

- If you are using pyramid_tm or the ZopeTransactionManager, your minimal
  integration is done. (The pages are ugly, but working. Keep reading...)


Need to session.commit()?
=========================

*pluserable* does not require pyramid_tm or the ZopeTransactionManager with your
session but if you do not use them you do have to take one extra step.
We don't commit transactions for you because that just wouldn't be nice!

All you have to do is subscribe to the extension events and
commit the session yourself. This also gives you the chance to
do some extra processing::

    from pluserable.events import (
        EventRegistration, EventActivation, EventLogin,
        EventPasswordReset, EventProfileUpdated,
    )

    def handle_event(event):
        request = event.request
        session = request.registry.getUtility(IDBSession)
        session.commit()

    kerno.events.subscribe(handle_event, EventRegistration)
    kerno.events.subscribe(handle_event, EventActivation)
    kerno.events.subscribe(handle_event, EventLogin)
    kerno.events.subscribe(handle_event, EventPasswordReset)
    kerno.events.subscribe(handle_event, EventProfileUpdated)

The ``kerno`` variable comes from your initialization of the kerno library,
which is useful to define the domain model of your application.
(The ``kerno`` variable represents a global object for the domain model --
it does not know anything about the web framework.)
At runtime pluserable finds the kerno instance at ``request.kerno``.
In the future pluserable will be independent of the Pyramid web framework.


Whether or not to have a "username" field
=========================================

It is important that you analyze the characteristics of your web application
and decide whether you need a ``username`` field for users to log in with.
pluserable provides 2 modes of operation:

- **email + username:** The user chooses a username when registering and later she can log in by providing either the username or the email address. Therefore, usernames may NOT contain the @ character. **This mode is the default.** It is expressed by the configuration setting ``pluserable.handle = usermail``
- **email only:** There is no ``username`` field and users only provide their email address. You enable this mode by:
    - Making your User model subclass NoUsernameMixin instead of UsernameMixin;
    - Adding this configuration setting: ``pluserable.handle = email``, which will make pluserable default to schemas that contain email fields instead of username fields.

If you make this change and want to keep your data you must deal with the
existing (or missing) "username" column yourself.


Changing the forms
==================

If you would like to modify any of the forms, you just need
to register the new deform class to be used.

The interfaces you have available to override from pluserable.interfaces are:

- IPluserableLoginForm
- IPluserableRegisterForm
- IPluserableForgotPasswordForm
- IPluserableResetPasswordForm
- IPluserableProfileForm

This is how you would do it (*MyForm* being a custom deform Form class)::

    config.registry.registerUtility(MyForm, IPluserableLoginForm)


Changing the templates
======================

If you would like to substitute the templates you can use pyramid's
`override_asset <http://pyramid.readthedocs.org/en/latest/narr/assets.html#overriding-assets-section>`_::

    config.override_asset(to_override="pluserable:templates/template.mako",
        override_with="your_package:templates/anothertemplate.mako")

The templates you have available to override are:

- login.mako
- register.mako
- forgot_password.mako
- reset_password.mako
- profile.mako

If you would like to override the templates with Jinja2, or any other
templating language, just override the view configuration::

    config.add_view("pluserable.views.AuthController", attr="login",
        route_name="login", renderer="yourapp:templates/login.jinja2")
    config.add_view("pluserable.views.ForgotPasswordController",
        attr="forgot_password", route_name="forgot_password",
        renderer="yourapp:templates/forgot_password.jinja2")
    config.add_view("pluserable.views.ForgotPasswordController",
        attr="reset_password", route_name="reset_password",
        renderer="yourapp:templates/reset_password.jinja2")
    config.add_view("pluserable.views.RegisterController", attr="register",
        route_name="register", renderer="yourapp:templates/register.jinja2")
    config.add_view("pluserable.views.ProfileController", attr="profile",
        route_name="profile", renderer="yourapp:templates/profile.jinja2")


Changing strings
================

Take a look at `this class
<https://github.com/nandoflorestan/pluserable/blob/master/pluserable/strings.py>`_.
This is where we store all the strings in *pluserable*.
If you'd like to change one or two messages, simply create a subclass
and configure it::

    [kerno utilities]
        # (...bla bla bla...)

        # Determining the UI strings is as easy as pointing to a class:
        string class = pluserable.strings:UIStringsBase

Here is an example implementation of a strings class::

    class AuthStrings(UIStringsBase):
        """Our alterations to the pluserable UI text."""

        login_done = None   # Do not flash a message after the user logs in
        logout_done = None  # Do not flash a message after the user logs out


Changing the email messages
===========================

*pluserable* includes functions that send very simple, plain text only,
email messages using pyramid_mailer.  Messages are sent synchronously.

You can replace those with your own functions in order to send emails
asynchronously (e. g. using celery), or to determine the content of the
email messages.  Plug your function in through kerno utilities -- for example
in configuration::

    [kerno utilities]
    pluserable.send_activation_email = myapp.actions:send_activation_email
    pluserable.send_reset_password_email = myapp.actions:send_reset_password_email

...or imperatively in startup code::

    eko.utilities.register(
        "pluserable.send_activation_email",
        "myapp.actions:send_activation_email"
    )
    eko.utilities.register(
        "pluserable.send_reset_password_email",
        "myapp.actions:send_reset_password_email"
    )


Changing the primary key column name
====================================

If you wish to override the primary key attribute name, you can do so
by creating a new mixin class::

    class NullPkMixin(Base):
        abstract = True
        _idAttribute = "pk"

        @declared_attr
        def pk(self):
            return Base.pk

        @declared_attr
        def id(self):
            return None

    class User(NullPkMixin, UserMixin):
        pass


pluserable development
======================

See https://github.com/nandoflorestan/pluserable

If you would like to help make any changes to *pluserable*, you can run its
unit tests with py.test:

    py.test

To check test coverage::

    py.test --cov-report term-missing --cov pluserable

The tests can also be run in parallel::

    py.test -n4

We are going to use this build server:
http://travis-ci.org/#!/nandoflorestan/pluserable


Origin of the project
=====================

*pluserable* started as a fork of *horus* by John Anderson:
https://github.com/eventray/horus

*horus* is no longer maintained since 2015.  *pluserable* is maintained and
sees 1 or 2 releases per year.
