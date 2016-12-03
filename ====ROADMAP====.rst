==================
pluserable roadmap
==================

- Models should not see the request object; move all I/O to a Repository layer
- Remove IUserClass, IActivationClass, IGroupClass, IUIStrings, schemas and forms
- Rethink the base model in light of the repository.
- Move certain modules into web/pyramid/
- Should the repository be a subclass of bag.sqlalchemy.context:SAContext?
- Create a ZODB repository in order to validate the interfaces
- Go through the TODOs on the code
- Refactor views: Create an action layer (also known as service layer)
- Test or remove the edit_profile() view.
- Do not create tables when running unit tests.
- Evaluate our test coverage.
- Move up subtransaction trick for tests. Or ditch it if we can rely on flush() only.
- Does Mundi need a request concept?
- Document the Repository.
- Remove FormValidationFailure exception
- Add civilized way of selecting which routes/views I want for my project
- Refactor sending emails with the strategy pattern
- Lose pyramid_mailer, but provide a mail backend that uses it
- Lose pystache
- Lose mako and pyramid_mako (at least as required dependencies)
- Lose deform, but keep colander
- Lose webtest by preferring unit tests

- Document

- Integrate velruse for sure
- Support Mozilla Persona?
- Demand Python 3.5 and use https://docs.python.org/3/library/typing.html
