# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (C) 2013 PolyBeacon, Inc.
#
# Author: Paul Belanger <paul.belanger@polybeacon.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from cliff import app
from cliff import commandmanager

from stripeclient import client
from stripeclient.common import exception
from stripeclient.common import utils
from stripeclient.openstack.common import log as logging
from stripeclient import version

LOG = logging.getLogger(__name__)


class Shell(app.App):

    def __init__(self, apiversion='1'):
        super(Shell, self).__init__(
            description='Stripe client', version=version.VERSION_INFO,
            command_manager=commandmanager.CommandManager('stripe.shell'),
        )

        self.api_version = apiversion

    def authenticate_user(self):
        if not self.options.ksp_username:
            raise exception.CommandError(
                'You must provide a username via either --ksp-username or '
                'env[KSP_USERNAME]')
        if not self.options.ksp_password:
            raise exception.CommandError(
                'You must provide a password via either --ksp-password or '
                'env[KSP_PASSWORD]')
        if not self.options.stripe_url:
            raise exception.CommandError(
                'You must provide a url via either --stripe-url or '
                'env[STRIPE_URL]')

        self.http_client = client.get_client(
            self.api_version, **(self.options.__dict__))

        return

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(Shell, self).build_option_parser(
            description, version, argparse_kwargs
        )

        parser.add_argument(
            '--ksp-auth-token', default=utils.env('KSP_AUTH_TOKEN'),
            help='Defaults to env[KSP_AUTH_TOKEN]')
        parser.add_argument(
            '--ksp-auth-url', default=utils.env('KSP_AUTH_URL'),
            help='Defaults to env[KSP_AUTH_URL]')
        parser.add_argument(
            '--ksp-password', default=utils.env('KSP_PASSWORD'),
            help='Defaults to env[KSP_PASSWORD]')
        parser.add_argument(
            '--ksp-tenant-id', default=utils.env('KSP_TENANT_ID'),
            help='Defaults to env[KSP_TENANT_ID]')
        parser.add_argument(
            '--ksp-tenant-name', default=utils.env('KSP_TENANT_NAME'),
            help='Defaults to env[KSP_TENANT_NAME]')
        parser.add_argument(
            '--ksp-username', default=utils.env('KSP_USERNAME'),
            help='Defaults to env[KSP_USERNAME]')
        parser.add_argument(
            '--stripe-url', default=utils.env('STRIPE_URL'),
            help='Defaults to env[STRIPE_URL]')

        return parser

    def initialize_app(self, argv):
        super(Shell, self).initialize_app(argv)

        logging.setup('stripeclient')
        cmd_name = None

        if argv:
            cmd_info = self.command_manager.find_command(argv)
            cmd_factory, cmd_name, sub_argv = cmd_info

        if self.interactive_mode or cmd_name != 'help':
            self.authenticate_user()


def main(argv=sys.argv[1:]):
    return Shell().run(argv)
