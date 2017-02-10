#!/usr/bin/env python3

"""Installer for pluserable."""

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def content_of(*files, encoding='utf-8'):
    """Return the content of ``files`` (which should be paths)."""
    here = os.path.abspath(os.path.dirname(__file__))
    content = []
    for f in files:
        with open(os.path.join(here, f), encoding=encoding) as stream:
            content.append(stream.read())
    return '\n'.join(content)


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        # self.test_args = []
        # self.test_suite = True

    def run_tests(self):
        # Import here, because outside the eggs aren't loaded
        import pytest
        result = pytest.main(self.test_args)
        sys.exit(result)


requires = [
    'bag > 0.8.0',
    'kerno',
    'sqlalchemy',       # TODO REMOVE when agnostic
    'zope.sqlalchemy',  # TODO REMOVE when agnostic
    'transaction',
    'cryptacular',
    'deform',
    'pyramid',          # TODO REMOVE when agnostic
    'pyramid_mailer',
    'pyramid_deform',
    'pyramid_mako',
]

setup(
    name='pluserable',
    version='0.3.0',
    description='Generic user registration for the Pyramid web framework',
    long_description=content_of('README.rst'),
    classifiers=[  # http://pypi.python.org/pypi?:action=list_classifiers
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    author='Nando Florestan',
    author_email='nandoflorestan@gmail.com',
    url='https://github.com/nandoflorestan/pluserable',
    keywords=[
        'authentication', 'horus', 'pyramid', 'user', 'registration'],
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires + ['pytest', 'mock', 'webtest'],
    cmdclass={'test': PyTest},
    test_suite='tests',
)
