==================
pluserable roadmap
==================

- Do not create tables when running unit tests.
- Move up subtransaction trick for tests.
- Does Mundi need a request concept?
- Refactor views: Create an action layer (also known as service layer)
- Models should not see the request object; move all I/O to a Repository layer
- Remove IUserClass, IActivationClass, IGroupClass, get_by_code
- Document the Repository.
- Move certain modules into web/pyramid/
- Use base model from bag library.
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
