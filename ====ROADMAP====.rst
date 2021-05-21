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
- Add @kerno_page and use it instead of @kerno_view.
- Use kerno.to_dict
- Stop the configuration madness.
- Rename NoUsernameMixin to BasicUserMixin and UsernameMixin to NamedUserMixin.
- Use the pydantic library, or the schema library, to validate configuration
- Add civilized way of selecting which routes/views I want for my project
- Lose schema and form interfaces; document
- Go through the TODOs on the code
- Extract more actions from views
- Move views into web/pyramid/. What about exceptions?
- Remove FormValidationFailure exception
- Refactor sending emails with the strategy pattern
- Lose mako and pyramid_mako (at least as required dependencies)
- Tests should use only the repository, never the session directly.
- Document -- especially the Repository.
- Keep our test coverage up.


Features
========

- Integrate velruse so we will have login via Facebook, Google etc.
