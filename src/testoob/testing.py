def _run_command_subprocess(args, input=None):
    from subprocess import Popen, PIPE
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    stdout, stderr = p.communicate(input)
    return stdout, stderr, p.returncode

def _run_command_popen2(args, input=None):
    import popen2
    quoted_args = ["'%s'" % arg for arg in args]
    child = popen2.Popen3(" ".join(quoted_args), capturestderr=True)

    if input is not None:
        child.tochild.write(input)

    rc = child.wait()

    return child.fromchild.read(), child.childerr.read(), rc

def _has_subprocess_module():
    try:
        import subprocess
        return True
    except ImportError:
        return False

def _run_command(args, input=None):
    """_run_command(args, input=None) -> stdoutstring, stderrstring, returncode
    Runs the command, giving the input if any.
    The command is specified as a list: 'ls -l' would be sent as ['ls', '-l'].
    Returns the standard output and error as strings, and the return code"""
    pass # the real implementation is below

# choose the proper implementation
if _has_subprocess_module(): _run_command = _run_command_subprocess
else:                        _run_command = _run_command_popen2

def assert_equals(expected, actual, msg = None):
    "works like unittest.TestCase.assertEquals"
    if expected == actual: return
    if msg is None:
        msg = '%s != %s' % (expected, actual)
    raise AssertionError(msg)

def assert_matches(regex, actual, msg=None):
    "fail unless regex matches actual (using re.search)"
    import re
    if re.search(regex, actual) is not None: return

    if msg is None:
        msg = "'%(actual)s' doesn't match regular expression '%(regex)s'" % vars()
    raise AssertionError(msg)

def conditionally_assert_equals(expected, actual):
    "assert_equals only if expected is not None"
    if expected is not None:
        assert_equals(expected, actual)

def conditionally_assert_matches(expected_regex, actual):
    "assert_matches only if expected_regex is not None"
    if expected_regex is not None:
        assert_matches(expected_regex, actual)

def command_line(
        args,
        input=None,
        expected_output=None,
        expected_error=None,
        expected_output_regex=None,
        expected_error_regex=None,
        expected_rc=0,):

    # TODO: make errors print full status like working directory, etc.

    # run command
    output, error, rc = _run_command(args, input)

    if expected_output is None and expected_output_regex is None:
        expected_output = ""
    if expected_error is None and expected_error_regex is None:
        expected_error = ""

    # test
    conditionally_assert_equals(expected_error, error)
    conditionally_assert_equals(expected_output, output)
    conditionally_assert_matches(expected_output_regex, output)
    conditionally_assert_matches(expected_error_regex, error)
    conditionally_assert_equals(expected_rc, rc)
