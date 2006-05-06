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

"An unittest-compatible Python testing framework"

__author__ = 'The TestOOB Team'
__version__ = '0.9'

from main import main
import testing

# Make every assert call the "addAssert" method of a reporter.
from asserter import Asserter
Asserter().make_asserts_report("unittest", "TestCase", "(^assert)|(^fail[A-Z])|(^fail$)")

from collecting import *