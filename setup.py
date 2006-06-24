kwargs = {
    'packages' : ['testoob', 'testoob.compatibility', 'testoob.reporting', 'testoob.running', 'testoob.commandline'],
    'package_dir' : {'': 'src'},
    'scripts'  : ['src/testoob/testoob'],

    # meta-data
    'name'             : 'testoob',
    'version'          : '1.1',
    'author'           : 'Ori Peleg',
    'author_email'     : 'testoob@gmail.com',
    'url'              : 'http://testoob.sourceforge.net',
    'download_url'     : 'http://sourceforge.net/project/showfiles.php?group_id=138557',
    'license'          : 'Apache License, Version 2.0',
    'platforms'        : ['any'],
    'description'      : 'Testoob - An advanced unit testing framework',
}


kwargs['long_description'] = """
Testoob - Python Testing Out Of (The) Box

Testoob is an advanced unit testing framework for Python. It
integrates effortlessly with existing PyUnit (module "unittest") test
suites.

Many bugs have been fixed in this release, and performance has been
improved.

New features include profiling support, a convenient summary of failed
tests, enhanced assertion of exceptions, graceful handling of Ctrl-C,
silent running, a simple GUI progress report, and enhanced skipping
support when testing command-line applications.

The changelog is available at:
http://sourceforge.net/project/shownotes.php?release_id=427357&group_id=138557
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
