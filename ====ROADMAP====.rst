==================
pluserable roadmap
==================

- Should the repository be a subclass of bag.sqlalchemy.context:SAContext?
- Create a ZODB repository in order to validate the interfaces
- Document the Repository.
- Go through the TODOs on the code
- Lose schema and form interfaces; document
- Extract actions from views
- Move views into web/pyramid/. What about events and exceptions?
- Evaluate our test coverage.
- Does Mundi need a request concept?
- Remove FormValidationFailure exception
- Add civilized way of selecting which routes/views I want for my project
- Refactor sending emails with the strategy pattern
- Lose pyramid_mailer, but provide a mail backend that uses it
- Lose pystache
- Lose mako and pyramid_mako (at least as required dependencies)
- Document
- Integrate velruse for sure
- Support Mozilla Persona?
- Demand Python 3.5 and use https://docs.python.org/3/library/typing.html
- Move up subtransaction trick for tests.
  Or ditch it (done in branch "no_subtransaction").
- New git repo
