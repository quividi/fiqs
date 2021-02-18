# -*- coding: utf-8 -*-

from os.path import join, dirname
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist


VERSION = (0, 5, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))


f = open(join(dirname(__file__), 'README.md'))
long_description = f.read().strip()
f.close()


install_requires = [
    'elasticsearch>=7.0.0,<8.0.0',
    'elasticsearch-dsl>=7.0.0,<8.0.0',
]
setup_requires = [
    'Babel>=2.3.4',
]
tests_require = [
    'Faker==0.7.3',
    'pytest==5.3.2',
    'pytest-cov==2.8.1',
    'sh==1.12.14',
]


class Sdist(sdist):
    """Custom ``sdist`` command to ensure that mo files are always created."""

    def run(self):
        self.run_command('compile_catalog')
        # sdist is an old style class so super cannot be used.
        sdist.run(self)


setup(
    name='fiqs',
    description="Python client for Elasticsearch "
                "built on top of elasticsearch-dsl",
    license="MIT License",
    url="https://github.com/pmourlanne/fiqs",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=__versionstr__,
    author="Pierre Mourlanne",
    author_email="pmourlanne@gmail.com",
    packages=find_packages(
        where='.',
    ),
    install_requires=install_requires,
    setup_requires=setup_requires,
    cmdclass={'sdist': Sdist},
    test_suite='fiqs.tests.run_tests.run_all',
    tests_require=tests_require,
)
