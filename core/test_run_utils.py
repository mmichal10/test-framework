#
# Copyright(c) 2019 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause-Clear
#


import pytest
from IPy import IP

from connection.ssh_executor import SshExecutor
from connection.local_executor import LocalExecutor
from storage_devices.disk import Disk
from test_utils import disk_finder
from test_utils.dut import Dut
from core.plugins import PluginManager
from log.base_log import test_failed
import core.test_run
import traceback


TestRun = core.test_run.TestRun


@classmethod
def __configure(cls, config):
    config.addinivalue_line(
        "markers",
        "require_disk(name, type): require disk of specific type, otherwise skip"
    )
    config.addinivalue_line(
        "markers",
        "require_plugin(name, *kwargs): require specific plugins, otherwise skip"
    )
    config.addinivalue_line(
        "markers",
        "remote_only: run test only in case of remote execution, otherwise skip"
    )


TestRun.configure = __configure


@classmethod
def __prepare(cls, item, config):
    if not config:
        raise Exception("You need to specify DUT config!")

    cls.item = item
    cls.config = config

    req_disks = list(map(lambda mark: mark.args, cls.item.iter_markers(name="require_disk")))
    cls.req_disks = dict(req_disks)
    if len(req_disks) != len(cls.req_disks):
        raise Exception("Disk name specified more than once!")


TestRun.prepare = __prepare


@classmethod
def __setup_disk(cls, disk_name, disk_type):
    cls.disks[disk_name] = next(filter(
        lambda disk: disk.disk_type in disk_type.types() and disk not in cls.disks.values(),
        cls.dut.disks
    ))
    if not cls.disks[disk_name]:
        pytest.skip("Unable to find requested disk!")
    cls.disks[disk_name].remove_partitions()


TestRun.__setup_disk = __setup_disk


@classmethod
def __setup_disks(cls):
    cls.disks = {}
    items = list(cls.req_disks.items())
    while items:
        resolved, unresolved = [], []
        for disk_name, disk_type in items:
            (resolved, unresolved)[not disk_type.resolved()].append((disk_name, disk_type))
        resolved.sort(
            key=lambda disk: (lambda disk_name, disk_type: disk_type)(*disk)
        )
        for disk_name, disk_type in resolved:
            cls.__setup_disk(disk_name, disk_type)
        items = unresolved


TestRun.__setup_disks = __setup_disks


@classmethod
def __setup(cls):
    cls.plugin_manager = PluginManager(cls.item, cls.config)
    cls.plugin_manager.hook_pre_setup()

    if cls.config['type'] == 'ssh':
        try:
            IP(cls.config['ip'])
        except ValueError:
            TestRun.block("IP address from config is in invalid format.")

        port = cls.config.get('port', 22)

        if 'user' in cls.config and 'password' in cls.config:
            cls.executor = SshExecutor(
                cls.config['ip'],
                cls.config['user'],
                cls.config['password'],
                port
            )
        else:
            TestRun.block("There are no credentials in config.")
    elif cls.config['type'] == 'local':
        cls.executor = LocalExecutor()
    else:
        TestRun.block("Execution type (local/ssh) is missing in DUT config!")

    if list(cls.item.iter_markers(name="remote_only")):
        if not cls.executor.is_remote():
            pytest.skip()

    Disk.plug_all_disks()
    if cls.config.get('allow_disk_autoselect', False):
        cls.config["disks"] = disk_finder.find_disks()

    try:
        cls.dut = Dut(cls.config)
    except Exception as ex:
        raise Exception(f"Failed to setup DUT instance:\n"
                        f"{str(ex)}\n{traceback.format_exc()}")
    cls.__setup_disks()

    cls.plugin_manager.hook_post_setup()


TestRun.setup = __setup


@classmethod
def __makereport(cls, item, call, res):
    cls.outcome = res.outcome

    from _pytest.outcomes import Failed
    from core.test_run import Blocked
    if res.when == "call" and res.failed:
        msg = f"{call.excinfo.type.__name__}: {call.excinfo.value}"
        if call.excinfo.type is Failed:
            cls.LOGGER.error(msg)
        elif call.excinfo.type is Blocked:
            cls.LOGGER.blocked(msg)
        else:
            cls.LOGGER.exception(msg)

    if res.when == "call" and test_failed(cls.LOGGER.get_result()):
        res.outcome = "failed"
        # To print additional message in final test report, assgin it to res.longrepr


TestRun.makereport = __makereport


@classmethod
def __teardown(cls):
    cls.plugin_manager.hook_teardown()


TestRun.teardown = __teardown
