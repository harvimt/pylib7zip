# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import os
import sys
from distutils.command.build import build

from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.test import test

base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "src")

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, src_dir)

about = {}
with open(os.path.join(src_dir, "lib7zip", "__about__.py")) as f:
    exec(f.read(), about)

requirements = [
    "cffi>=0.9",
    "setuptools",
    "future",
]

if sys.version_info < (3, 4):
    requirements.append("enum34")

# If you add a new dep here you probably need to add it in the tox.ini as well
test_requirements = [
    "pytest",
]


def get_ext_modules():
    import lib7zip._lib7zip
    return [lib7zip._lib7zip.ffi.verifier.get_extension()]


class CFFIBuild(build):

    """
    This class exists, instead of just providing ``ext_modules=[...]`` directly
    in ``setup()`` because importing cryptography requires we have several
    packages installed first.

    By doing the imports here we ensure that packages listed in
    ``setup_requires`` are already installed.
    """

    def finalize_options(self):
        self.distribution.ext_modules = get_ext_modules()
        build.finalize_options(self)


class CFFIInstall(install):

    """
    As a consequence of CFFIBuild and it's late addition of ext_modules, we
    need the equivalent for the ``install`` command to install into platlib
    install-dir rather than purelib.
    """

    def finalize_options(self):
        self.distribution.ext_modules = get_ext_modules()
        install.finalize_options(self)


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here because in module scope the eggs are not loaded.
        import pytest
        test_args = [os.path.join(base_dir, "tests")]
        errno = pytest.main(test_args)
        sys.exit(errno)


def keywords_with_side_effects(argv):

    """
    Get a dictionary with setup keywords that (can) have side effects.

    :param argv: A list of strings with command line arguments.
    :returns: A dictionary with keyword arguments for the ``setup()`` function.

    This setup.py script uses the setuptools 'setup_requires' feature because
    this is required by the cffi package to compile extension modules. The
    purpose of ``keywords_with_side_effects()`` is to avoid triggering the cffi
    build process as a result of setup.py invocations that don't need the cffi
    module to be built (setup.py serves the dual purpose of exposing package
    metadata).

    All of the options listed by ``python setup.py --help`` that print
    information should be recognized here. The commands ``clean``,
    ``egg_info``, ``register``, ``sdist`` and ``upload`` are also recognized.
    Any combination of these options and commands is also supported.

    This function was originally based on the `setup.py script`_ of SciPy (see
    also the discussion in `pip issue #25`_).

    .. _pip issue #25: https://github.com/pypa/pip/issues/25
    .. _setup.py script: https://github.com/scipy/scipy/blob/master/setup.py
    """
    no_setup_requires_arguments = (
        '-h', '--help',
        '-n', '--dry-run',
        '-q', '--quiet',
        '-v', '--verbose',
        '-V', '--version',
        '--author',
        '--author-email',
        '--classifiers',
        '--contact',
        '--contact-email',
        '--description',
        '--egg-base',
        '--fullname',
        '--help-commands',
        '--keywords',
        '--licence',
        '--license',
        '--long-description',
        '--maintainer',
        '--maintainer-email',
        '--name',
        '--no-user-cfg',
        '--obsoletes',
        '--platforms',
        '--provides',
        '--requires',
        '--url',
        'clean',
        'egg_info',
        'register',
        'sdist',
        'upload',
    )

    def is_short_option(argument):
        """Check whether a command line argument is a short option."""
        return len(argument) >= 2 and argument[0] == '-' and argument[1] != '-'

    def expand_short_options(argument):
        """Expand combined short options into canonical short options."""
        return ('-' + char for char in argument[1:])

    def argument_without_setup_requirements(argv, i):
        """Check whether a command line argument needs setup requirements."""
        if argv[i] in no_setup_requires_arguments:
            # Simple case: An argument which is either an option or a command
            # which doesn't need setup requirements.
            return True
        elif (is_short_option(argv[i]) and
              all(option in no_setup_requires_arguments
                  for option in expand_short_options(argv[i]))):
            # Not so simple case: Combined short options none of which need
            # setup requirements.
            return True
        elif argv[i - 1:i] == ['--egg-base']:
            # Tricky case: --egg-info takes an argument which should not make
            # us use setup_requires (defeating the purpose of this code).
            return True
        else:
            return False

    if all(argument_without_setup_requirements(argv, i)
           for i in range(1, len(argv))):
        return {
            "cmdclass": {
                "build": DummyCFFIBuild,
                "install": DummyCFFIInstall,
                "test": DummyPyTest,
            }
        }
    else:
        return {
            "setup_requires": requirements,
            "cmdclass": {
                "build": CFFIBuild,
                "install": CFFIInstall,
                "test": PyTest,
            }
        }


setup_requires_error = ("Requested setup command that needs 'setup_requires' "
                        "while command line arguments implied a side effect "
                        "free command or option.")


class DummyCFFIBuild(build):

    """
    This class makes it very obvious when ``keywords_with_side_effects()`` has
    incorrectly interpreted the command line arguments to ``setup.py build`` as
    one of the 'side effect free' commands or options.
    """

    def run(self):
        raise RuntimeError(setup_requires_error)


class DummyCFFIInstall(install):

    """
    This class makes it very obvious when ``keywords_with_side_effects()`` has
    incorrectly interpreted the command line arguments to ``setup.py install``
    as one of the 'side effect free' commands or options.
    """

    def run(self):
        raise RuntimeError(setup_requires_error)


class DummyPyTest(test):

    """
    This class makes it very obvious when ``keywords_with_side_effects()`` has
    incorrectly interpreted the command line arguments to ``setup.py test`` as
    one of the 'side effect free' commands or options.
    """

    def run_tests(self):
        raise RuntimeError(setup_requires_error)


with open(os.path.join(base_dir, "README.rst")) as f:
    long_description = f.read()


setup(
    name=about["__title__"],
    version=about["__version__"],

    description=about["__summary__"],
    long_description=long_description,
    license=about["__license__"],
    url=about["__uri__"],

    author=about["__author__"],
    author_email=about["__email__"],

    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License "
        "v2 or later (LGPLv2+)",
        "Natural Language :: English",
        # "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        # "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        # "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        # "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        # "Programming Language :: Python :: Implementation :: PyPy",
    ],

    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests", "tests.*"]),

    install_requires=requirements,
    tests_require=test_requirements,

    # for cffi
    zip_safe=False,
    ext_package="lib7zip",
    **keywords_with_side_effects(sys.argv)
)
