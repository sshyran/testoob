"test running logic"

import unittest as _unittest
from extracting import suite_iter as _suite_iter

###############################################################################
# apply_runner
###############################################################################
from extracting import extract_fixtures as _extract_fixtures
import time
def apply_runner(suites, runner, reporter, interval=None, test_extractor=None):
    """Runs the suite."""
    if test_extractor is None: test_extractor = _extract_fixtures

    runner.set_result(reporter)

    reporter.start()
    first = True
    for suite in _suite_iter(suites):
        for fixture in test_extractor(suite):
            if not first and interval is not None:
                time.sleep(interval)
            first = False
            runner.run(fixture)
    reporter.done()

###############################################################################
# Runners
###############################################################################

class SimpleRunner:
    def __init__(self):
        self._result = None

    def run(self, fixture):
        fixture(self._result)

    def set_result(self, result):
        self._result = result

def run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    run_suites(suites, **kwargs)

def run_suites(suites, reporters, runner_class=SimpleRunner, addError=None, **kwargs):
    "Run the test suites"

    from reporting import ReporterProxy
    reporter_proxy = ReporterProxy()
    for reporter in reporters:
        if addError != None:
            real_addError = reporter.addError
            reporter.addError = lambda test, err: addError(test, err, reporter, real_addError)
        reporter_proxy.add_observer(reporter)

    apply_runner(suites=suites,
                 runner=runner_class(),
                 reporter=reporter_proxy,
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
    Accepts keyword 'verbosity' (0, 1, or 2, default is 1)
    and 'immediate' (True or False)
    """

    verbosity = _pop(kwargs, "verbosity", 1)
    immediate = _pop(kwargs, "immediate", False)

    kwargs.setdefault("reporters", [])

    import sys, reporting
    reporter_class = _pop(kwargs, "reporter_class", reporting.TextStreamReporter)
    kwargs["reporters"].append( reporter_class(
            verbosity=verbosity,
            immediate=immediate,
            descriptions=1,
            stream=sys.stderr) )

    run(*args, **kwargs)



