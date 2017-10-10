==================
pluserable roadmap
==================

**pluserable** is in the middle of a great refactoring right now. It is working
fine, but the way you configure it is changing. Hopefully this will be
finished in the next release. The resulting code will be much more
flexible and maintainable.


Refactoring
===========

- Stop the configuration madness.
- Add civilized way of selecting which routes/views I want for my project
- Lose schema and form interfaces; document
- Go through the TODOs on the code
- Extract actions from views
- Move views into web/pyramid/. What about events and exceptions?
- Remove FormValidationFailure exception
- Refactor sending emails with the strategy pattern
- Lose mako and pyramid_mako (at least as required dependencies)
- Tests should use only the repository, never the session directly.
- Document -- especially the Repository.
- Demand Python 3.5 and use https://docs.python.org/3/library/typing.html
- Keep our test coverage up.


Features
========

- Integrate velruse so we will have login via Facebook, Google etc.
- Create a ZODB repository in order to validate the interfaces.
- Support Mozilla Persona?
- New git repo
