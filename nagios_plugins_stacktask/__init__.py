# Copyright (C) 2016 Catalyst IT Ltd
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import os

from nagios_plugins_stacktask import check_stacktask


def main():
    command = os.path.basename(sys.argv[0])
    try:
        if command.startswith('check_') and hasattr(check_stacktask, command):
            func = getattr(check_stacktask, command)
            return func()
    except Exception as e:
        print "CRITICAL: Failed to get status from Stacktask (%s)" % e
        return 2

    print "UNKNOWN: Nagios check '%s' unimplemented!" % command
    return 3
