# Testoob, Python Testing Out Of (The) Box
# Copyright (C) 2005-2006 The Testoob Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"Some useful test-collecting functions"

from __future__ import generators

try:
    from itertools import ifilter as _ifilter
except ImportError:
    from compatibility.itertools import ifilter as _ifilter

from os.path import dirname, normpath

def _is_test_case(x):
    import types, unittest
    try:
        return issubclass(x, unittest.TestCase)
    except TypeError:
        # x isn't a class
        return False

def collect(globals_dict):
    import warnings
    warnings.warn(
        "'collect' has been renamed to 'collector_from_globals'",
        category=DeprecationWarning
    )
    return collector_from_globals(globals_dict)
def collector_from_globals(globals_dict):
    """
    Returns a function that collects all TestCases from the given globals
    dictionary, and registers them in a new TestSuite, returning it.
    """
    import unittest
    def suite():
        result = unittest.TestSuite()
        for test_case in _ifilter(_is_test_case, globals_dict.values()):
            result.addTest(unittest.makeSuite(test_case))
        return result
    return suite

def collect_from_modules(modules, globals_dict):
    import warnings
    warnings.warn(
        "'collect_from_modules' has been renamed to 'collector_from_modules'",
        category=DeprecationWarning
    )
    return collector_from_modules(modules, globals_dict)
def collector_from_modules(modules, globals_dict):
    """
    Returns a function that collects all TestCases from the given module name
    list, and the given globals dictionary, and registers them in a new
    TestSuite, returning it.
    """
    import unittest
    def suite():
        result = unittest.TestSuite()
        for modulename in modules:
            NONEMPTYLIST = [None] # help(__import__) says we need this.
            result.addTest(
                __import__(modulename, globals_dict, None, NONEMPTYLIST).suite()
            )
        return result
    return suite

def _frame_filename(frame):
    if '__file__' in frame.f_globals:
        return frame.f_globals["__file__"]

    # backwards compatability
    return frame.f_code.co_filename

def _first_external_frame():
    import sys

    current_file = _frame_filename( sys._getframe() )

    # find the first frame with a filename different than this one
    frame = sys._getframe()
    while _frame_filename(frame) == current_file:
        frame = frame.f_back

    return frame

def _calling_module_name():
    return _first_external_frame().f_globals["__name__"]

def _calling_module_directory():
    return normpath(dirname(_first_external_frame().f_code.co_filename))

def _module_names(glob_pattern, modulename, path):
    import glob
    from os.path import splitext, basename, join
    return [
        modulename + "." + splitext(basename(filename))[0]
        for filename in glob.glob( join(path, glob_pattern) )
    ]

def _load_suite(module_name):
    import unittest
    result = unittest.TestLoader().loadTestsFromName( module_name )
    if len(result._tests) == 0:
        import warnings
        warnings.warn("No tests loaded for module '%s'" % module_name)
    return result

def collect_from_files(glob_pattern, name=None, modulename=None, path=None, file=None):
    if name is not None and modulename is not None:
        raise ValueError("conflicting arguments 'name' and 'modulename' can't be specified together")

    if modulename is not None:
        warnings.warn("'modulename' parameter name is deprecated, use 'name' instead")
        name = modulename

    if name is None:
        name = _calling_module_name()

    if path is not None and file is not None:
        raise ValueError("conflicting arguments 'path' and 'file' can't be specified together")

    if path is None:
        if file is None:
            path = _calling_module_directory()
        else:
            path = dirname(file)

    # mimicking unittest.TestLoader.loadTestsFromNames, but with more checks
    suites = [
        _load_suite(name)
        for name in _module_names(glob_pattern, name, path)
    ]

    import unittest
    return unittest.TestLoader().suiteClass(suites)
