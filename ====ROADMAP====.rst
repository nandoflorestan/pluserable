==================
pluserable roadmap
==================


Refactoring
===========

- Move the ``pluserable.handle`` setting to validated configuration.
- Rename NoUsernameMixin to BasicUserMixin and UsernameMixin to NamedUserMixin.
- Use kerno.state instead of bag's add_flash(). Document.
- Stop depending on bag's SettingsReader class.
- Add @kerno_page and use it instead of @kerno_view.
- Use kerno.to_dict
- Start using Pyramid2 security policies
- Add civilized way of selecting which routes/views I want for my project
- Lose schema and form interfaces; document
- Go through the TODOs on the code
- Extract more actions from views
- Remove FormValidationFailure exception
- Refactor sending emails with the strategy pattern
- Lose mako and pyramid_mako (at least as required dependencies)
- Tests should use only the repository, never the session directly.
- Keep our test coverage up.


Features
========

- Login via Facebook, Google etc. - maybe through velruse


If brute force prevention were through the database instead of redis
--------------------------------------------------------------------

::

    ip_address table:
        ip: string
        blocked_since: date
        blocked_reason: string
        user_ids: set[int]

We would need a Celery task to periodically delete old blocked ips.
