# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 Ori Peleg, Barak Schiller, and Misha Seltzer
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

"test running logic"

import unittest as _unittest
from extracting import suite_iter as _suite_iter

###############################################################################
# apply_runner
###############################################################################
from extracting import full_extractor as _full_extractor
import time

def apply_decorators(callable, decorators):
    "Wrap the callable in all the decorators"
    result = callable
    for decorator in decorators:
        result = decorator(result)
    return result

def apply_runner(suites, runner, interval=None, extraction_decorators = None):
    """Runs the suite."""

    if extraction_decorators is None: extraction_decorators = []
    test_extractor = apply_decorators(_full_extractor, extraction_decorators)

    first = True
    for suite in _suite_iter(suites):
        for fixture in test_extractor(suite):
            if not first and interval is not None:
                time.sleep(interval)
            first = False
            runner.run(fixture)
    runner.done()

###############################################################################
# Runners
###############################################################################

class BaseRunner(object):
    """default implementations of setting a reporter and done()"""
    def __init__(self):
        from asserter import Asserter
        self._Asserter = Asserter

    def _set_reporter(self, reporter):
        self._reporter = reporter
        self._reporter.start()
    reporter = property(lambda self:self._reporter, _set_reporter)

    def run(self, fixture):
        # Let the assert functions know it's reporter.
        self._Asserter().set_reporter(fixture, self._reporter)

    def done(self):
        self.reporter.done()

class SimpleRunner(BaseRunner):
    def run(self, fixture):
        BaseRunner.run(self, fixture)
        fixture(self._reporter)

class ThreadedRunner(BaseRunner):
    """Run tests using a threadpool.
    Uses TwistedPython's thread pool"""
    def __init__(self, max_threads=None):
        BaseRunner.__init__(self)

        from twisted.python.threadpool import ThreadPool

        min_threads = min(ThreadPool.min, max_threads)
        self.pool = ThreadPool(minthreads = min_threads, maxthreads=max_threads)
        self.pool.start()

    def run(self, fixture):
        BaseRunner.run(self, fixture)
        self.pool.dispatch(None, fixture, self.reporter)

    def done(self):
        self.pool.stop()
        BaseRunner.done(self)

class ProcessedRunner(BaseRunner):
    "Run tests using fork in different processes."
    def __init__(self, max_processes=1):
        from processed_helper import ProcessedRunnerHelper
        BaseRunner.__init__(self)
        self._helper = ProcessedRunnerHelper(max_processes)

    def run(self, fixture):
        BaseRunner.run(self, fixture)
        self._helper.register_fixture(fixture)

    def done(self):
        self._helper.start(self.reporter)
        BaseRunner.done(self)

class _FixtureInfo:
    def __init__(self, fixture):
        self.fixture = fixture
    
    def module(self):
        return self.fixture.__module__

    def filename(self):
        import sys
        try:
            return sys.modules[self.module()].__file__
        except KeyError:
            return "unknown file"

    def classname(self):
        return self.fixture.__class__.__name__

    def funcname(self):
        # parsing id() because the function name is a private fixture field
        return self.fixture.id().split(".")[-1]

    def docstring(self):
        if getattr(self.fixture, self.funcname()).__doc__:
            return getattr(self.fixture, self.funcname()).__doc__.splitlines()[0]
        return ""

    def funcinfo(self):
        return (self.funcname(), self.docstring())

class _TestHistory:
    def __init__(self):
        self.modules = {}

    def record_fixture(self, fixture):
        """Store the info about each fixture, to show them later.
        """
        fixture_info = _FixtureInfo(fixture)
        self._class_function_list(fixture_info).append(fixture_info.funcinfo())

    def get_string(self, max_functions_to_show):
        """Show the test methods, if there are too many list the classes only.
        """
        result = []
        for (module_name, module_info) in self.modules.items():
            result.append("Module: %s (%s)" % \
                    (module_name, module_info["filename"]))
            for (class_name, functions) in module_info["classes"].items():
                result.append("\tClass: %s (%d test functions)" %\
                      (class_name, len(functions)))
                if self._num_functions() <= max_functions_to_show:
                    for func in functions:
                        result.append("\t\t%s()%s" % \
                                (func[0], func[1] and " - "+func[1] or ""))
        return "\n".join(result)

    def _module(self, fixture_info):
        self.modules.setdefault(
                fixture_info.module(),
                {
                    "filename": fixture_info.filename(),
                    "classes": {}
                })
        return self.modules[fixture_info.module()]

    def _class_function_list(self, fixture_info):
        classes_dict = self._module(fixture_info)["classes"]
        classes_dict.setdefault(fixture_info.classname(), [])
        return classes_dict[fixture_info.classname()]

    def _num_functions(self):
        result = 0
        for mod_info in self.modules.values():
            for functions in mod_info["classes"].values():
                result += len(functions)
        return result

class ListingRunner(BaseRunner):
    """Just list the test names, don't run them.
    """
    
    def __init__(self):
        self.history = _TestHistory()

    def run(self, fixture):
        self.history.record_fixture(fixture)

    def done(self):
        print self.history.get_string(max_functions_to_show=50)

def run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    # Make every assert call the "addAssert" method of a reporter.
    from asserter import Asserter
    Asserter().make_asserts_report("unittest", "TestCase", "(^assert)|(^fail[A-Z])|(^fail$)")

    run_suites(suites, **kwargs)

def _apply_debug(reporter, runDebug):
    if runDebug is None:
        return reporter

    def replace(reporter, flavor, methodname):
        original = getattr(reporter, methodname)
        def replacement(test, err):
            runDebug(test, err, flavor, reporter, original)
        setattr(reporter, methodname, replacement)

    replace(reporter, "error", "addError")
    replace(reporter, "failure", "addFailure")

    return reporter

def _create_reporter_proxy(reporters, runDebug):
    from reporting import ReporterProxy
    result = ReporterProxy()
    for reporter in reporters:
        result.add_observer(_apply_debug(reporter, runDebug))
    return result

def run_suites(suites, reporters, runner=None, runDebug=None, **kwargs):
    "Run the test suites"
    runner = runner or SimpleRunner()
    runner.reporter = _create_reporter_proxy(reporters, runDebug)
    
    apply_runner(suites=suites,
                 runner=runner,
                 **kwargs)

###############################################################################
# text_run
###############################################################################

def _pop(d, key, default):
    try:
        return d.pop(key, default)
    except AttributeError:
        pass

    # In Python 2.2 we'll implement pop ourselves
    try:
        return d.get(key, default)
    finally:
        if key in d: del d[key]

def text_run(*args, **kwargs):
    """
    Run suites with a TextStreamReporter.
    Accepts keyword 'verbosity' (0, 1, 2 or 3, default is 1)
    and 'immediate' (True or False)
    """

    verbosity = _pop(kwargs, "verbosity", 1)
    immediate = _pop(kwargs, "immediate", False)

    kwargs.setdefault("reporters", [])

    import sys, reporting
    reporter_class = _pop(kwargs, "reporter_class", reporting.TextStreamReporter)

    reporter_instance = reporter_class(
            verbosity=verbosity,
            immediate=immediate,
            descriptions=1,
            stream=sys.stderr)

    kwargs["reporters"].append(reporter_instance)

    run(*args, **kwargs)
    return reporter_instance.getDoneStatus()

