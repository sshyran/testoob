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

"main() implementation"

def _arg_parser(usage):
    try:
        import optparse
    except ImportError:
        from compatibility import optparse

    formatter=optparse.TitledHelpFormatter(max_help_position=30)
    p = optparse.OptionParser(usage=usage, formatter=formatter)
    p.add_option("--version", action="store_true", help="Print the version of testoob")
    p.add_option("-q", "--quiet",   action="store_true", help="Minimal output")
    p.add_option("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_option("-i", "--immediate", action="store_true", help="Immediate feedback about exceptions")
    p.add_option("--vassert", action="store_true", help="Make asserts verbose")
    p.add_option("-l", "--list", action="store_true", help="List the test classes and methods found")
    p.add_option("--regex", help="Filtering regular expression")
    p.add_option("--glob", metavar="PATTERN", help="Filtering glob pattern")
    p.add_option("--xml", metavar="FILE", help="output results in XML")
    p.add_option("--html", metavar="FILE", help="output results in HTML")
    p.add_option("--color", action="store_true", help="Color output")
    p.add_option("--interval", metavar="SECONDS", type="float", default=0, help="Add interval between tests")
    p.add_option("--timeout", metavar="SECONDS", type="int", help="Fail test if passes timeout")
    p.add_option("--stop-on-fail", action="store_true", help="Stop tests on first failure")
    p.add_option("--debug", action="store_true", help="Run pdb on tests that fail on Error")
    p.add_option("--threads", metavar="NUM_THREADS", type="int", help="Run in a threadpool")
    p.add_option("--processes", metavar="NUM_PROCESSES", type="int", help="Run in multiple processes, use Pyro if available")
    p.add_option("--processes_pyro", metavar="NUM_PROCESSES", type="int", help="Run in multiple processes, requires Pyro")
    p.add_option("--processes_old", metavar="NUM_PROCESSES", type="int", help="Run in multiple processes, old implementation")
    p.add_option("--repeat", metavar="NUM_TIMES", type="int", help="Repeat each test")

    options, parameters = p.parse_args()
    if options.version:
        from __init__ import __version__
        print __version__
        from sys import exit
        exit(0)
    
    return p

def _get_verbosity(options):
    if options.quiet: return 0
    if options.vassert: return 3
    if options.verbose: return 2
    return 1

def _get_suites(suite, defaultTest, test_names):
    if suite is not None:
        # an explicit suite always wins
        return [suite]

    from unittest import TestLoader
    import __main__
    if len(test_names) == 0 and defaultTest is None:
        # load all tests from __main__
        return TestLoader().loadTestsFromModule(__main__)

    if len(test_names) == 0:
        test_names = [defaultTest]
    return TestLoader().loadTestsFromNames(test_names, __main__)

class ArgumentsError(Exception): pass

def _main(suite, defaultTest, options, test_names, parser):

    def require_modules(option, *modules):
        missing_modules = []
        for modulename in modules:
            try:
                __import__(modulename)
            except ImportError:
                missing_modules.append(modulename)
        if missing_modules:
            raise ArgumentsError(
                    "option '%(option)s' requires missing modules "
                    "%(missing_modules)s" % vars())

    def require_posix(option):
        try:
            import posix
        except ImportError:
            raise ArgumentsError("option '%s' requires a POSIX environment" % option)

    def conflicting_options(*option_names):
        given_options = [
            name
            for name in option_names
            if getattr(options, name) is not None
        ]
        given_options.sort()

        if len(given_options) > 1:
            raise ArgumentsError(
                    "The following options can't be specified together: %s" %
                    ", ".join(given_options))

    conflicting_options("threads", "timeout")
    conflicting_options("threads", "processes", "processes_old", "processes_pyro", "stop_on_fail")
    conflicting_options("threads", "processes", "processes_old", "processes_pyro", "list") # specify runners
    conflicting_options("processes", "processes_old", "processes_pyro", "debug")

    kwargs = {
        "suites" : _get_suites(suite, defaultTest, test_names),
        "verbosity" : _get_verbosity(options),
        "immediate" : options.immediate,
        "stop_on_fail" : options.stop_on_fail,
        "reporters" : [],
        "extraction_decorators" : [],
        "interval" : options.interval,
    }
    kwargs.setdefault("timeout", 0)

    if options.timeout is not None:
        kwargs["timeout"] = options.timeout
        def alarm(sig, stack_frame):
            raise AssertionError("Timeout")
        import signal
        signal.signal(signal.SIGALRM, alarm)

    if options.regex is not None:
        import extracting
        kwargs["extraction_decorators"].append(extracting.regex(options.regex))

    if options.list is not None:
        from running import ListingRunner
        kwargs["runner"] = ListingRunner()

    if options.glob is not None:
        import extracting
        kwargs["extraction_decorators"].append(extracting.glob(options.glob))

    if options.repeat is not None:
        import extracting
        kwargs["extraction_decorators"].append(extracting.repeat(options.repeat))

    if options.xml is not None:
        from reporting import XMLFileReporter
        kwargs["reporters"].append( XMLFileReporter(filename=options.xml) )

    if options.html is not None:
        require_modules("--html", "Ft.Xml")
        from reporting import HTMLReporter
        kwargs["reporters"].append( HTMLReporter(filename=options.html) )

    if options.color is not None:
        from reporting import ColoredTextReporter
        kwargs["reporter_class"] = ColoredTextReporter

    if options.debug is not None:
        import pdb
        def runDebug(test, err_info, flavour, reporter, real_add):
            from signal import alarm
            alarm(0) # Don't timeout on debug.
            assert flavour in ("error", "failure")
            real_add(test, err_info)
            print "\nDebugging for %s in test: %s" % (
                    flavour, reporter.getDescription(test))
            pdb.post_mortem(err_info.traceback())
        kwargs["runDebug"] = runDebug

    if options.threads is not None:
        require_modules("--threads", "twisted.python.threadpool")
        from running import ThreadedRunner
        kwargs["runner"] = ThreadedRunner(max_threads = options.threads)

    def enable_processes_pyro(nprocesses):
        require_posix("--processes_pyro")
        require_modules("--processes_pyro", "Pyro")
        from running import PyroRunner
        kwargs["runner"] = PyroRunner(max_processes = nprocesses)

    def enable_processes_old(nprocesses):
        require_posix("--processes_old")
        from running import ProcessedRunner
        kwargs["runner"] = ProcessedRunner(max_processes = nprocesses)

    if options.processes_pyro is not None:
        enable_processes_pyro(options.processes_pyro)
        
    if options.processes_old is not None:
        enable_processes_old(options.processes_old)

    if options.processes is not None:
        try:
            enable_processes_pyro(options.processes)
        except ArgumentsError:
            enable_processes_old(options.processes)

    import running
    return running.text_run(**kwargs)

def main(suite=None, defaultTest=None):
    usage="""%prog [options] [test1 [test2 [...]]]

examples:
  %prog                          - run default set of tests
  %prog MyTestSuite              - run suite 'MyTestSuite'
  %prog MyTestCase.testSomething - run MyTestCase.testSomething
  %prog MyTestCase               - run all 'test*' test methods in MyTestCase"""

    parser = _arg_parser(usage)
    options, test_names = parser.parse_args()

    try:
        return _main(suite, defaultTest, options, test_names, parser)
    except ArgumentsError, e:
        parser.error(str(e))
