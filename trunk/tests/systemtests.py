import helpers
helpers.fix_include_path()

import unittest, testoob

_suite_file = helpers.project_subpath("tests/suites.py")

def _create_args(testcase=None, options=None):
    import sys
    result = [sys.executable, helpers.executable_path(), _suite_file]
    if options is not None: result += options
    if testcase is not None: result.append(testcase)
    return result

class CommandLineTestCase(unittest.TestCase):
    def testSuccesfulRunNormal(self):
        args = _create_args(options=[], testcase="CaseDigits")
        regex = r"""
\.\.\.\.\.\.\.\.\.\.
----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testSuccesfulRunQuiet(self):
        args = _create_args(options=["-q"], testcase="CaseDigits")
        regex = r"""
^----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK$
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testSuccesfulRunVerbose(self):
        args = _create_args(options=["-v"], testcase="CaseDigits")
        regex = r"""
test0 \(.*suites\.CaseDigits\.test0\) \.\.\. ok
test1 \(.*suites\.CaseDigits\.test1\) \.\.\. ok
test2 \(.*suites\.CaseDigits\.test2\) \.\.\. ok
test3 \(.*suites\.CaseDigits\.test3\) \.\.\. ok
test4 \(.*suites\.CaseDigits\.test4\) \.\.\. ok
test5 \(.*suites\.CaseDigits\.test5\) \.\.\. ok
test6 \(.*suites\.CaseDigits\.test6\) \.\.\. ok
test7 \(.*suites\.CaseDigits\.test7\) \.\.\. ok
test8 \(.*suites\.CaseDigits\.test8\) \.\.\. ok
test9 \(.*suites\.CaseDigits\.test9\) \.\.\. ok

----------------------------------------------------------------------
Ran 10 tests in \d\.\d+s
OK
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testFailureRunQuiet(self):
        args = _create_args(options=["-q"], testcase="CaseFailure")
        regex = r"""
^======================================================================
FAIL: testFailure \(.*suites\.CaseFailure\.testFailure\)
----------------------------------------------------------------------
.*AssertionError

----------------------------------------------------------------------
Ran 1 test in \d\.\d+s
FAILED \(failures=1\)$
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testRegex(self):
        args = _create_args(options=["-v", "--regex=A|D|J"], testcase="CaseLetters")
        regex=r"""
testA \(.*suites\.CaseLetters\.testA\) \.\.\. ok
testD \(.*suites\.CaseLetters\.testD\) \.\.\. ok
testJ \(.*suites\.CaseLetters\.testJ\) \.\.\. ok
""".strip()

        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertSimple(self):
        args = _create_args(options=["--regex=CaseDigits.test0", "--vassert"])
        regex = r"""
test0 \(suites\.CaseDigits\.test0\) \.\.\. ok
  \[ PASSED \(assertEquals\) first: "00" second: "00" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)

    def testVassertFormatStrings(self):
        args = _create_args(options=["--regex=MoreTests.test.*FormatString",
                                     "--vassert"])
        regex = r"""
test.*FormatString \(suites\.MoreTests\.test.*FormatString\) \.\.\. ok
  \[ PASSED \(assertEquals\) first: "%s" second: "%s" \]

----------------------------------------------------------------------
""".strip()
        testoob.testing.command_line(args=args, expected_error_regex=regex)


def suite(): return unittest.makeSuite(CommandLineTestCase)
if __name__ == "__main__": unittest.main()
