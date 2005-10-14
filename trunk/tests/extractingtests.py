import helpers
import unittest
import testoob.extracting
import suites

class ExtractingTestCase(helpers.TestoobBaseTestCase):
    def _runWithDecorator(self, decorator):
        self._run(suite=suites.suite(), extraction_decorators=[decorator])

    def testRegexExtractorMatchEverything(self):
        self._runWithDecorator(testoob.extracting.regex_extractor(".*"))
        self._check_reporter(
                started   = suites.all_test_names,
                finished  = suites.all_test_names,
                successes = suites.all_test_names,
                failures  = [],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

    def testRegexExtractorMatchSome(self):
        self._runWithDecorator(testoob.extracting.regex_extractor("(B|C|6)$"))
        self._check_reporter(
                started   = ["testB", "testC", "test6"],
                finished  = ["testB", "testC", "test6"],
                successes = ["testB", "testC", "test6"],
                failures  = [],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

    def testRegexExtractorMatchNone(self):
        self._runWithDecorator(testoob.extracting.regex_extractor("xanadu"))
        self._check_reporter(
                started   = [],
                finished  = [],
                successes = [],
                failures  = [],
                errors    = [],
                stdout    = "",
                stderr    = "",
            )

def suite(): return unittest.makeSuite(ExtractingTestCase)

if __name__ == "__main__": unittest.main()
