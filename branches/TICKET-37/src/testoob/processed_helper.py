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

class ProcessedRunnerHelper:
    "A helper class to make ProcessedRunner shorter and clearer."
    def __init__(self, max_processes):
        self._fixturesList = [[] for i in xrange(max_processes)]
        self._load_balance_idx = 0

    def register_fixture(self, fixture):
        self._fixturesList[self._load_balance_idx].append(fixture)
        self._load_balance_idx = (self._load_balance_idx + 1) % len(self._fixturesList)

    def start(self, reporter):
        from os import fork, pipe, fdopen
        from sys import exit

        children = []

        for processFixtures in self._fixturesList:
            pipePair = [(fdopen(r, 'r'), fdopen(w, 'w')) for r, w in [pipe()]][0]
            pid = fork()
            if pid == 0:
                pipePair[0].close()
                pipeReporter = self._create_pipeReporter(pipePair[1])
                self._run_fixtures(processFixtures, pipeReporter)
                pipePair[1].close()
                exit()
            pipePair[1].close()
            children.append({"pid": pid, "pipe": pipePair[0]})

        self._listen(reporter, children)

    def _run_fixtures(self, fixtures, reporter):
        [fixture(reporter) for fixture in fixtures]

    def _create_pipeReporter(self, writePipe):
        from reporting import ProcessedReporter
        # TODO: better implemintation.
        return ProcessedReporter(writePipe)

    def _listen(self, reporter, children):
        from base64 import decodestring
        from cPickle import loads
        from os import waitpid
        from select import select
        while children:
            ready = select([child["pipe"] for child in children], [], [])[0]
            for childsPipe in ready:
                received = childsPipe.readline().split(" ")
                if received == ['']:
                    child = [child for child in children if child["pipe"] == childsPipe][0]
                    waitpid(child["pid"], 0)
                    children.remove(child)
                    continue
                received[1:] = map(lambda x: loads(decodestring(eval(x))), received[1:])
                try:
                    getattr(reporter, received[0])(*received[1:])
                except Exception, e:
                    pass # TODO: do something here...

