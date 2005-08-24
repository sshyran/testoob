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

"Test running"

import unittest as _unittest
from extracting import suite_iter as _suite_iter

###############################################################################
# apply_runner
###############################################################################
from extracting import extract_fixtures as _extract_fixtures
import time
def apply_runner(suites, runner, interval=None, test_extractor = _extract_fixtures):
    """
    Runs the suite
    
    @param suites: an iterable with test suites, or a C{unittest.TestSuite}
                   instance
    @param runner: the runner to use to run the tests
    @param interval: the amount of time to wait between tests
    @param test_extractor: the callable used to extract fixtures from a suite,
                           should return an iterable. Default is L{extracting.extract_fixtures}
    """
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
    """
    Default implementations for runners.
    """
    def _set_reporter(self, reporter):
        self._reporter = reporter
        self._reporter.start()
    reporter = property(
            lambda self:self._reporter, _set_reporter,
            doc="""
            The reporter used by the runner

            Usually a L{reporting.ReporterProxy}"""
        )

    def run(self, fixture):
        """
        Run the fixture.

        @param fixture: the test fixture to run, a callable object that accepts
                        a L{reporter <reporting.IReporter>} as a parameter.
                        C{unittest} test fixtures are fine.
        """
        # just to remind you :-)
        raise NotImplementedError

    def done(self):
        """Called when the running is done"""
        self.reporter.done()

class SimpleRunner(BaseRunner):
    """Simply each fixture with the reporter"""
    def run(self, fixture):
        """Simply call the fixture with the reporter"""
        fixture(self._reporter)

class ThreadedRunner(BaseRunner):
    """
    Run tests using a threadpool

    Uses Twisted's thread pool.
    """
    def __init__(self, max_threads=None):
        """
        @param max_threads: the maximum number of threads in the thread pool
        """
        BaseRunner.__init__(self)

        from twisted.python.threadpool import ThreadPool

        min_threads = min(ThreadPool.min, max_threads)
        self.pool = ThreadPool(minthreads = min_threads, maxthreads=max_threads)
        self.pool.start()

    def run(self, fixture):
        """Have one of the threads call the fixture with the reporter"""
        self.pool.dispatch(None, fixture, self.reporter)

    def done(self):
        """Stop the thread pool"""
        self.pool.stop()
        BaseRunner.done(self)

def run(suite=None, suites=None, **kwargs):
    """
    Convenience frontend for L{run_suites}
    """
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

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
    """
    Run the test suites

    Unknown keyword arguments will be forwarded to L{apply_runner}.

    @param reporters: the reporters to report to
    @param runner: the runner to use, default is L{SimpleRunner}
    @param runDebug: should a debugger spawn on errors?
    """
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
    Run suites with a L{reporting.TextStreamReporter}

    Frontend to L{run}.

    @keyword verbosity: one of 0, 1, 2, or 3, default is 1
    @keyword immediate: flag, should errors be reported immediately?
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

    if verbosity == 3:
        import verbalize
        verbalize.make_methods_verbose("unittest",
                                       "TestCase",
                                       "(^assert)|(^fail[A-Z])|(^fail$)",
                                       reporter_instance)

    kwargs["reporters"].append(reporter_instance)

    run(*args, **kwargs)

