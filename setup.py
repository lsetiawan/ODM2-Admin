import os
import sys
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.verbose = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def extract_version(module='ODM2CZOData'):
    version = None
    fdir = os.path.dirname(__file__)
    fnme = os.path.join(fdir, module, '__init__.py')
    with open(fnme) as fd:
        for line in fd:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                # Remove quotation characters.
                version = version.strip()[1:-1]
                break
    return version


rootpath = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return open(os.path.join(rootpath, *parts), 'r').read()


long_description = '{}'.format(read('README.rst'))

with open('requirements.txt') as f:
    require = f.readlines()
install_requires = [r.strip() for r in require]

setup(name='odm2djangoadmin',
      version=extract_version(),
      license='MIT License',
      long_description=long_description,
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Education',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Education',
                   ],
      description='Django admin app for Observation Data Model 2 (ODM2)',
      url='https://github.com/miguelcleon/ODM2-Admin',
      platforms='any',
      keywords=['ODM2', 'Django'],
      install_requires=install_requires,
      packages=find_packages(),
      include_package_data=True,
      tests_require=['pytest'],
      cmdclass=dict(test=PyTest),
      author=['Miguel Leon'],
      author_email='leonmi@sas.upenn.edu',
      entry_points='''
        [console_scripts]
        runserver_odm2admin=runserver.runserver_odm2admin:cli
      '''
      )
