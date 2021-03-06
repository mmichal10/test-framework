#
# Copyright(c) 2019 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause-Clear
#


import logging
import pytest
from api.cas import casadm
from test_package.conftest import base_prepare


LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize("shortcut", [True, False])
@pytest.mark.parametrize('prepare_and_cleanup',
                         [{"core_count": 0, "cache_count": 0}],
                         indirect=True)
def test_cli_help(prepare_and_cleanup, shortcut):
    prepare()
    LOGGER.info("Test run")
    output = casadm.help(shortcut)
    LOGGER.info(output.stdout)  # TODO:this is tmp, every ssh command shall be logged via executor
    assert output.stdout[0:33] == "Cache Acceleration Software Linux"
    # TODO: create yml config for every help command and match the output with it
    # TODO: for now the assert above is purely for testing flow in the casadm api


def prepare():
    base_prepare()
