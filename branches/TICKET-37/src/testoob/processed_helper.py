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

class ProcessedRunnerHelper():
    "A helper class to make ProcessedRunner shorter and clearer."
    def __init__(self, max_processes):
        self._fixturesList = [[]] * max_processes
        self._load_balance_idx = 0

    def register_fixture(self, fixture):
        self._fixturesList[self._load_balance_idx].append(value)
        self._load_balance_idx = (self._load_balance_idx + 1) % len(self._fixturesList)

    def start(self, reporter):
        from os import fork as _os_fork, pipe as _os_pipe, fdopen as _os_fdopen
        from sys import exit as _sys_exit

        children = []

        for processFixtures in self._fixturesList:
            pipePair = map(_os_fdopen, _os_pipe())
            pid = _os_fork()
            if pid == 0:
                pipeReporter = self._create_pipeReporter(pipePair[1])
                self._run_fixtures(processFixtures, pipeReporter)
                _sys_exit()
            children.append({"pid": pid, "pipe": pipePair[0]})

        self._listen(reporter, children)

    def _run_fixtures(self, fixtures, reporter):
        [fixture(reporter) for fixture in fixtures]

    def _create_pipeReporter(self, writeFD):
        # TODO: implement.
        pass

    def _listen(self, reporter, children):
        from base64 import decodestring
        from cPickle import loads
        from os import waitpid
        while children:
            for child in children:
                if child["pipe"].closed(): # TODO implement rightly.
                    waitpid(child["pid"], 0)
                    children.remove(child)
                elif child["pipe"].can_read(): # TODO implement rightly.
                    received = child["pipe"].readline().split(" ")
                    received[1:] = map(lambda x: loads(decodestring(x)), received[1:])
                    try:
                        getattr(reporter, received[0])(*received[1:])
                    except Exception, e:
                        pass # TODO: do something here...

