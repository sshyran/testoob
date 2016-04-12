# Feature List #
```
Usage
=====
  testoob [options] [test1 [test2 [...]]]

examples:
  testoob                          - run default set of tests
  testoob MyTestSuite              - run suite 'MyTestSuite'
  testoob MyTestCase.testSomething - run MyTestCase.testSomething
  testoob MyTestCase               - run all 'test*' test methods in MyTestCase

Options
=======
--version                     show program's version number and exit
--help, -h                    show this help message and exit
--bgcolor=WHEN                What's the background color of the terminal.
                              This is used to determine a readable warning
                              color. Choices are ['auto', 'light', 'dark'],
                              default is 'auto'
--color-mode=WHEN             When should output be in color? Choices are
                              ['never', 'always', 'auto'], default is 'auto'
--glob=PATTERN                Filtering glob pattern
--html=FILE                   output results in HTML
--immediate, -i               Immediate feedback about exceptions
--list, -l                    List the test classes and methods found
--list-formatted=FORMATTER    Like option '-l', just formatted (e.g. csv).
--pbar                        Show a progress bar
--pdf=FILE                    output results in PDF (requires ReportLab)
--processes=NUM_PROCESSES     Run in multiple processes, use Pyro if available
--processes_pyro=NUM_PROCESSES
                              Run in multiple processes, requires Pyro
--processes_old=NUM_PROCESSES
                              Run in multiple processes, old implementation
--randomize-order             Randomize the test order
--randomize-seed=SEED         Seed for randomizing the test order, implies
                              --randomize-order
--regex=REGEX                 Filtering regular expression
--repeat=NUM_TIMES            Repeat each test
--silent, -s                  no output to terminal
--timed-repeat=SECONDS        Repeat each test, for a limited time
--time-each-test              Report the total time for each test
--xml=FILE                    output results in XML
--quiet, -q                   Minimal output
--verbose, -v                 Verbose output
--vassert                     Make asserts verbose
--interval=SECONDS            Add interval between tests
--timeout=SECONDS             Fail test if passes timeout
--timeout-with-threads=SECONDS
                              Fail test if passes timeout, implemented with
                              threads
--stop-on-fail                Stop tests on first failure
--debug                       Run pdb on tests that fail
--threads=NUM_THREADS         Run in a threadpool
--capture                     Capture the output of the test, and show it only
                              if test fails
--coverage=AMOUNT             Test the coverage of the tested code, choices
                              are: ['silent', 'slim', 'normal', 'massive',
                              'xml']
--test-method-glob=PATTERN    Collect test methods based on a glob pattern
--test-method-regex=REGEX     Collect test methods based on a regular
                              expression
--profiler=PROFILER           Profile the tests with a profiler, choices are:
                              ['hotshot', 'profile']
--profdata=FILE               Target file for profiling information, default
                              is 'testoob.stats'
--rerun-on-fail               Used with --debug, rerun a failing test when
                              debugging it
```