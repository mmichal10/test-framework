#
# Copyright(c) 2019 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause-Clear
#


from log.logger import Log
import pytest


class Blocked(Exception):
    pass


class TestRun:
    dut = None
    executor = None
    LOGGER: Log = None
    plugins = {}

    @classmethod
    def step(cls, message):
        return cls.LOGGER.step(message)

    @classmethod
    def group(cls, message):
        return cls.LOGGER.group(message)

    @classmethod
    def iteration(cls, iterable, group_name=None):
        TestRun.LOGGER.start_group(f"{group_name}" if group_name is not None else "Iteration list")
        items = list(iterable)
        for i, item in enumerate(items, start=1):
            cls.LOGGER.start_iteration(f"Iteration {i}/{len(items)}")
            yield item
            TestRun.LOGGER.end_iteration()
        TestRun.LOGGER.end_group()

    @classmethod
    def fail(cls, message):
        pytest.fail(message)

    @classmethod
    def workaround(cls, message):
        if cls.LOGGER:
            cls.LOGGER.workaround(message)

    @classmethod
    def warning(cls, message):
        if cls.LOGGER:
            cls.LOGGER.warning(message)

    @classmethod
    def skip(cls, message):
        if cls.LOGGER:
            cls.LOGGER.skip(message)

    @classmethod
    def error(cls, message):
        if cls.LOGGER:
            cls.LOGGER.error(message)

    @classmethod
    def critical(cls, message):
        if cls.LOGGER:
            cls.LOGGER.critical(message)

    @classmethod
    def block(cls, message):
        raise Blocked(message)
