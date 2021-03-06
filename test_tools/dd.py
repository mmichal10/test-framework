#
# Copyright(c) 2019 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause-Clear
#

import test_utils.linux_command as linux_comm
import test_utils.size as size
from test_package.test_properties import TestProperties


class Dd(linux_comm.LinuxCommand):
    def __init__(self):
        linux_comm.LinuxCommand.__init__(self, TestProperties.executor, 'dd')

    def block_size(self, value: size.Size):
        return self.set_param('bs', int(value.get_value()))

    def count(self, value):
        return self.set_param('count', value)

    def input(self, value):
        return self.set_param('if', value)

    def iflag(self, *values):
        return self.set_param('iflag', *values)

    def oflag(self, *values):
        return self.set_param('oflag', *values)

    def output(self, value):
        return self.set_param('of', value)
