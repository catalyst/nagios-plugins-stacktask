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

from stacktaskclient import client as stacktask_client
from keystoneclient.v2_0 import client as ks_client
from keystoneauth1.identity import v2
from keystoneauth1 import session

import nagios_openstack_argparse


def create_os_client(arguments):

    def verify_to_bool(verify):
        """ Verify must be either a boolean or a string
            so we must convert, if we can.
         """
        # check for actual bool values
        if verify.lower() in ['true', 't', 'y', 'yes']:
            return True
        if verify.lower() in ['false', 'f', 'n', 'no']:
            return False
        # neither found, probably a path, then.
        return verify

    if not all([
        arguments.os_username,
        arguments.os_password,
        arguments.os_tenant_name,
        arguments.os_auth_url,
        arguments.os_region_name
            ]):
        print "UNKNOWN - All openstack arguments must be provided."
        sys.exit(3)
    verify = verify_to_bool(arguments.verify)
    auth = v2.Password(
        username=arguments.os_username,
        password=arguments.os_password,
        tenant_name=arguments.os_tenant_name,
        auth_url=arguments.os_auth_url
    )
    sess = session.Session(
        auth=auth,
        verify=verify,
        timeout=arguments.timeout)
    kc = ks_client.Client(session=sess)

    try:
        service = kc.services.find(type="registration")
        endpoint = kc.endpoints.find(
            service_id=service.id, region=arguments.os_region_name)
    except Exception as e:
        print "CRITICAL - Unable to query keystone for registration endpoint. (%s)" % e
        sys.exit(2)

    kwargs = {
        'auth_url': arguments.os_auth_url,
        'session': sess,
        'auth': auth,
        'service_type': "registration",
        'endpoint_type': "public",
        'region_name': arguments.os_region_name
    }

    client = stacktask_client.Client(1, endpoint.publicurl, **kwargs)
    return client


def check_stacktask_notifications():
    # Note(dale): use custom ArgumentParser to implement --extra-opts ini
    # and other --os-* arguments.
    parser = nagios_openstack_argparse.NagiosOpenstackArgparse()

    parser.add_argument(
        '-c', '--critical', metavar='error_count',
        type=int, default=5, required=False,
        help='Number of unack notifications considered CRITICAL.')
    parser.add_argument(
        '-w', '--warning', metavar='error_count',
        type=int, default=1, required=False,
        help='Number of unack notifications considered WARNING.')
    parser.add_argument(
        '--timeout', type=float, default=5, required=False,
        help='A timeout to pass to requests. This should be a numerical value indicating some amount (or fraction) of seconds. (optional, defaults to 5)')
    parser.add_argument(
        '--verify', default=True, required=False,
        help='The verification arguments to pass to keystone.Session and then requests. These are of the same form as requests expects, so True or False to verify (or not) against system certificates or a path to a bundle or CA certs to check against or None for requests to attempt to locate and use certificates. (optional, defaults to True)')
    parser.add_argument('-v', '--verbose', action='store_true')

    arguments = parser.parse_args()
    client = create_os_client(arguments)

    response = client.status.get()
    if response.status_code != 200:
        msg = "CRITICAL - Failed to get status from Stacktask ({code})."
        print msg.format(code=response.status_code)
        sys.exit(2)

    status = response.json()

    # First we check if there are any error notifications
    # and if they are over the threshold.
    unack_errors = len(status["error_notifications"])
    unack_string = "%d unacknowledged error notifications." % unack_errors
    if unack_errors >= arguments.critical:
        print "CRITICAL - " + unack_string
        sys.exit(2)

    if unack_errors >= arguments.warning:
        print "WARNING - " + unack_string
        sys.exit(1)

    print ("OK - " + unack_string)
    return 0
