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

"Code coverage module"

import trace, os, sys

class Coverage:
    """
    Python code coverage module built specifically for checking code coverage
    in tests performed by TestOOB.

    NOTE: This class depends on the 'trace' module.
    """
    def __init__(self, ignorepaths=()):
        """
        initialize the code coverage module, gets list of directories and files
        which's coverage is not needed.
        """
        # coverage is a dictinary mapping filenames to another dictionary with
        # the following keys:
        #    lines   - a set of number of executable lines in the file.
        #    covered - a set of numbers of executed lines in the file.
        self.coverage = {}
        self.ignorepaths = ignorepaths

    def runfunc(self, func, *args, **kwargs):
        "Gets a function and it's arguments to run and perform code coverage test"
        sys.settrace(self._tracer)
        try:
            return func(*args, **kwargs)
        finally:
            sys.settrace(None)

    def getstatistics(self):
        """
        Returns a dictionary of statistics. the dictionary maps between a filename
        and the statistics associated to it.

        The statistics dictionary has 3 keys:
            lines   - the number of executable lines in the file
            covered - the number of lines covered in the file
            percent - the percentage of covered lines.

        This dictionary also has a special "file" (key) called '__total__', which
        holds the statistics for all the files together.
        """
        statistics = {}
        for filename, coverage in self.coverage.items():
            statistics[filename] = {
                "lines"  : len(coverage["lines"]),
                "covered": len(coverage["covered"]),
                "percent": int(100 * len(coverage["covered"]) / len(coverage["lines"]))
            }
        return statistics

    def _sum_coverage(self, callable):
        "Helper method for _total_{lines,covered}"
        return sum([callable(coverage)
                    for coverage in self.coverage.values()])
    def total_lines(self):
        return self._sum_coverage(lambda coverage: len(coverage["lines"]))
    def total_lines_covered(self):
        return self._sum_coverage(lambda coverage: len(coverage["covered"]))
    def total_coverage_percentage(self):
        if self.total_lines() == 0:
            return 0
        return int(100 * self.total_lines_covered() / self.total_lines())

    def print_statistics(self):
        print "lines   cov_n   cov%   module   (path)"
        print "--------------------------------------"
        for filename, stats in self.getstatistics().items():
            print "%5d   %5d   %3d%%   %s   (%s)" % (
                stats["lines"], stats["covered"], stats["percent"], trace.modname(filename), filename)
        print "--------------------------------------"
        print "%5d   %5d   %3d%%   TOTAL" % (
            self.total_lines(), self.total_lines_covered(), self.total_coverage_percentage())

    def print_coverage(self):
        maxmodule = max(map(lambda x: len(trace.modname(x)), self.coverage.keys()))
        module_tmpl = "%%- %ds" % maxmodule
        print module_tmpl % "module" + "   lines   cov_n   cov%   missing"
        print "-" * maxmodule +        "---------------------------------"
        for filename, stats in self.getstatistics().items():
            print (module_tmpl + "   %5d   %5d   %3d%%   %s") % (
                trace.modname(filename), stats["lines"], stats["covered"], stats["percent"],
                self._get_missing_str(filename))
        print "-" * maxmodule +        "---------------------------------"
        print (module_tmpl + "   %5d   %5d   %3d%%") % ("TOTAL", self.total_lines(),
                self.total_lines_covered(), self.total_coverage_percentage())
            
    def _get_missing_str(self, filename):
        lines, covered = self.coverage[filename].values()
        return self._shrinker([line for line in covered if line not in lines])

    def _shrinker(self, l):
        l.sort()
        # adding a 'strange' value to the end of the list, so the last value
        # will be checked (iterating until (len(l) - 1)).
        l.append("")
        result = [""]
        for i in xrange(len(l) - 1):
            if l[i+1] == (l[i] + 1):
                if result[-1] == "":
                    result[-1] = str(l[i]) + "-"
            else:
                result[-1] += str(l[i])
                result.append("")
        result.pop()
        return result
    
    def _should_cover_frame(self, frame):
        "Should we check coverage for this file?"
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        for path in self.ignorepaths:
            if filename.startswith(path):
                return False
        
        if not self.coverage.has_key(filename):
            self.coverage[filename] = {
                "lines": set(trace.find_executable_linenos(filename)),
                "covered": set()
            }
        return lineno in self.coverage[filename]["lines"]
    
    def _tracer(self, frame, why, arg):
        "Trace function to be put as input for sys.settrace()"
        if self._should_cover_frame(frame):
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            self.coverage[filename]["covered"].add(lineno)

        return self._tracer

