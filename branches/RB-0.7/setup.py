kwargs = {
    'packages' : ['testoob', 'testoob.compatibility'],
    'package_dir' : {'': 'src'},
    'scripts'  : ['src/testoob/testoob'],

    # meta-data
    'name'             : 'testoob',
    'version'          : '0.7',
    'author'           : 'Ori Peleg',
    'author_email'     : 'testoob@gmail.com',
    'url'              : 'http://testoob.sourceforge.net',
    'download_url'     : 'http://sourceforge.net/project/showfiles.php?group_id=138557',
    'license'          : 'Apache License, Version 2.0',
    'platforms'        : ['any'],
    'description'      : 'TestOOB - An advanced unit testing framework',
}


kwargs['long_description'] = """
TestOOB - Python Testing Out Of (The) Box

TestOOB is an advanced unit testing framework for Python, designed
to integrate with existing unittest test suites.

New in version 0.7:
 * run tests in multiple processes!
 * repeat tests
 * filter tests with glob patterns
 * non-zero exit code on test failures
""".strip()

kwargs['classifiers'] = """
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Programming Language :: Python
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
""".strip().splitlines()

# ============================================================================

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
import sys
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# run setup
from distutils.core import setup

setup(**kwargs)
