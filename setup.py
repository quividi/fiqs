from os.path import dirname, join

from setuptools import find_packages, setup
from setuptools.command.sdist import sdist

VERSION = (0, 8, 5)
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))


f = open(join(dirname(__file__), "README.md"))
long_description = f.read().strip()
f.close()


install_requires = [
    "elasticsearch>=8.0.0,<9.0.0",
    "elasticsearch-dsl>=8.0.0,<9.0.0",
]
setup_requires = [
    "Babel>=2.14.0",
]
tests_require = [
    "Faker==24.4.0",
    "pytest==8.1.1",
    "pytest-cov==5.0.0",
    "sh==2.0.6",
]


class Sdist(sdist):
    """Custom ``sdist`` command to ensure that mo files are always created."""

    def run(self):
        self.run_command("compile_catalog")
        # sdist is an old style class so super cannot be used.
        sdist.run(self)


setup(
    name="fiqs",
    description="Python client for Elasticsearch " "built on top of elasticsearch-dsl",
    license="MIT License",
    url="https://github.com/pmourlanne/fiqs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__versionstr__,
    author="Pierre Mourlanne",
    author_email="pmourlanne@gmail.com",
    packages=find_packages(
        where=".",
    ),
    install_requires=install_requires,
    setup_requires=setup_requires,
    cmdclass={"sdist": Sdist},
    test_suite="fiqs.tests.run_tests.run_all",
    tests_require=tests_require,
)
