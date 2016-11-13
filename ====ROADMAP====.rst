==================
pluserable roadmap
==================

- import colander as c
- import deform as d
- Use base model from bag library.
- Lose hem
- Lose CSRFSchema in favor of Pyramid 1.7 updated CSRF protection.
- Add civilized way of selecting which routes/views I want for my project
- Models should not see the request object; move all I/O to a Repository layer
- Refactor views: Create an action layer (also known as service layer)
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
