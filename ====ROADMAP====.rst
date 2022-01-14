==================
pluserable roadmap
==================

**pluserable** is in the middle of a great refactoring right now. It is working
fine, but the way you configure it is changing. Hopefully this will be
finished in the next release. The resulting code will be much more
flexible and maintainable.


Refactoring
===========

- Use kerno.state instead of bag's add_flash(). Document.
- Stop depending on bag's SettingsReader class.
- Add @kerno_page and use it instead of @kerno_view.
- Use kerno.to_dict
- Rename NoUsernameMixin to BasicUserMixin and UsernameMixin to NamedUserMixin.
- Start using Pyramid2 security policies
- Add civilized way of selecting which routes/views I want for my project
- Lose schema and form interfaces; document
- Go through the TODOs on the code
- Extract more actions from views
- Remove FormValidationFailure exception
- Refactor sending emails with the strategy pattern
- Lose mako and pyramid_mako (at least as required dependencies)
- Tests should use only the repository, never the session directly.
- Document -- especially the Repository.
- Keep our test coverage up.


Features
========

- Prevent brute force attacks by storing IP addresses that failed authentication.
- Integrate velruse so we will have login via Facebook, Google etc.
