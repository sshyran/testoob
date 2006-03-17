kwargs = {
    'packages' : ['testoob', 'testoob.compatibility', 'testoob.reporting', 'testoob.running'],
    'package_dir' : {'': 'src'},
    'scripts'  : ['src/testoob/testoob'],

    # meta-data
    'name'             : 'testoob',
    'version'          : '0.9',
    'author'           : 'Ori Peleg',
    'author_email'     : 'testoob@gmail.com',
    'url'              : 'http://testoob.sourceforge.net',
    'download_url'     : 'http://sourceforge.net/project/showfiles.php?group_id=138557',
    'license'          : 'Apache License, Version 2.0',
    'platforms'        : ['any'],
    'description'      : 'testoob - an advanced testing framework',
}


kwargs['long_description'] = """
testoob - Python Testing Out Of (The) Box

'testoob' is an advanced testing framework for Python that is fully
compatible with existing PyUnit test suites.

Version 0.9 fixes some bugs and adds code coverage support, timed-repeat
of tests, improved testing of command-line applications, and several
more features.

A full list of changes is available at:
http://sourceforge.net/project/shownotes.php?release_id=402463&group_id=138557
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
