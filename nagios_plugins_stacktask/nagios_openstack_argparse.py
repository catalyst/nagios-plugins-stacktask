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

import argparse
import ConfigParser
import os


class NagiosOpenstackOpt(object):
    def __init__(self, arg, ini_opt, metavar, help_text):
        self.arg = arg
        self.ini_opt = ini_opt
        self.metavar = metavar
        self.help_text = help_text


class NagiosOpenstackArgparse(argparse.ArgumentParser):
    openstack_opts = [
        NagiosOpenstackOpt(
            '--os-username',
            'os_username',
            'OS_USERNAME',
            'Defaults to extra_opts ini, then env[OS_USERNAME].'),
        NagiosOpenstackOpt(
            '--os-password',
            'os_password',
            'OS_PASSWORD',
            'Defaults to extra_opts ini, then env[OS_PASSWORD].'),
        NagiosOpenstackOpt(
            '--os-tenant-name',
            'os_tenant_name',
            'OS_TENANT_NAME',
            'Defaults to extra_opts ini, then env[OS_TENANT_NAME].'),
        NagiosOpenstackOpt(
            '--os-auth-url',
            'os_auth_url',
            'OS_AUTH_URL',
            'Defaults to extra_opts ini, then env[OS_AUTH_URL].'),
        NagiosOpenstackOpt(
            '--os-region-name',
            'os_region_name',
            'OS_REGION_NAME',
            'Defaults to extra_opts ini, then env[OS_REGION_NAME].'),
    ]

    def __init__(self):
        super(NagiosOpenstackArgparse, self).__init__()
        self._add_openstack_parsers()
        self.extra_opt_values = {}

    def parse_args(self):
        arguments = super(NagiosOpenstackArgparse, self).parse_args()
        self._read_extra_opts(arguments)
        self._resolve_defaults(arguments)
        return arguments

    def _add_openstack_parsers(self):
        for opt in self.openstack_opts:
            self.add_argument(
                opt.arg,
                metavar=opt.metavar,
                default=None,
                help=opt.help_text)

        self.add_argument(
            '--extra-opts',
            metavar='INI_FILE:SECTION',
            help='Ini file and section to read before using environment variable defaults, useful for protecting credentials from command line arguments and environment variables.')

    def _resolve_defaults(self, arguments):
        for opt in self.openstack_opts:
            opt_name = opt.ini_opt
            if getattr(arguments, opt_name) is not None:
                # Specified in args, use those.
                continue
            if opt_name in self.extra_opt_values:
                # Use ini values
                setattr(arguments, opt_name,
                        self.extra_opt_values[opt_name])
            elif opt.metavar in os.environ:
                # Use env variables
                setattr(arguments, opt_name,
                        os.environ[opt.metavar])
            else:
                raise argparse.ArgumentError(
                    None,
                    "Openstack config option '%s' must be provided." % opt_name)

    def _read_extra_opts(self, arguments):
        """ Reads an INI format file into the extra_opt_values dict """
        if (not hasattr(arguments, 'extra_opts') or
                arguments.extra_opts is None):
            return arguments

        try:
            filename, section = arguments.extra_opts.split(':')
        except ValueError:
            msg = "Failed to parse extra_opts. Must be in <file>:<section> format."
            raise argparse.ArgumentError(None, msg)

        extra_parser = ConfigParser.RawConfigParser()
        if not extra_parser.read(filename):
            return

        for opt in self.openstack_opts:
            try:
                value = extra_parser.get(section, opt.ini_opt)
            except ConfigParser.NoOptionError:
                continue
            self.extra_opt_values[opt.ini_opt] = value
