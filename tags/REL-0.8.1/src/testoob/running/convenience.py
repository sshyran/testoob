# TestOOB, Python Testing Out Of (The) Box
# Copyright (C) 2005 The TestOOB Team
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

"convenience functions for running tests"

###############################################################################
# apply_runner
###############################################################################
from testoob.extracting import suite_iter as _suite_iter
from testoob.extracting import full_extractor as _full_extractor

def apply_decorators(callable, decorators):
    "Wrap the callable in all the decorators"
    result = callable
    for decorator in decorators:
        result = decorator(result)
    return result

def apply_runner(suites, runner, interval=None, stop_on_fail=False,
                 extraction_decorators = None, timeout=0):
    """Runs the suite."""
    if extraction_decorators is None: extraction_decorators = []
    test_extractor = apply_decorators(_full_extractor, extraction_decorators)

    class Alarmed_fixture:
        def __init__(self, fixture):
            self.alarm = lambda x:x
            if timeout:
                from signal import alarm
                self.alarm = alarm
            self.fixture = fixture
        
        def __call__(self, *args):
            self.alarm(timeout) # Set timeout for a fixture.
            self.fixture(*args)
            self.alarm(0) # Release the alarm that was set.

        def get_fixture(self):
            return self.fixture
    
    def running_loop():
        import time
        first = True
        for suite in _suite_iter(suites):
            for fixture in test_extractor(suite):
                if not first and interval is not None:
                    time.sleep(interval)
                first = False
                if not runner.run(Alarmed_fixture(fixture)) and stop_on_fail:
                    return

    running_loop()
    runner.done()
    return runner.isSuccessful()

###############################################################################
# run
###############################################################################
def run(suite=None, suites=None, **kwargs):
    "Convenience frontend for text_run_suites"
    if suite is None and suites is None:
        raise TypeError("either suite or suites must be specified")
    if suite is not None and suites is not None:
        raise TypeError("only one of suite or suites may be specified")

    if suites is None:
        suites = [suite]

    return run_suites(suites, **kwargs)

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
    from testoob.reporting import ReporterProxy
    result = ReporterProxy()
    for reporter in reporters:
        result.add_observer(_apply_debug(reporter, runDebug))
    return result

def run_suites(suites, reporters, runner=None, runDebug=None, **kwargs):
    "Run the test suites"
    if runner is None:
        from simplerunner import SimpleRunner
        runner = SimpleRunner()
    runner.reporter = _create_reporter_proxy(reporters, runDebug)
    
    return apply_runner(suites=suites,
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

    import sys
    from testoob.reporting import TextStreamReporter
    reporter_class = _pop(kwargs, "reporter_class", TextStreamReporter)

    reporter_instance = reporter_class(
            verbosity=verbosity,
            immediate=immediate,
            descriptions=1,
            stream=sys.stderr)

    kwargs["reporters"].append(reporter_instance)

    return run(*args, **kwargs)
