#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

import pytest

from jobcalc.config import env_strings as env

logger = logging.getLogger(__name__)


def _clean_up_env():
    logger.debug('cleaning env')
    for key in env:
        try:
            del(os.environ[key])
        except KeyError:
            pass


@pytest.fixture()
def clean_env():
    return _clean_up_env


@pytest.yield_fixture()
def test_env_setup(clean_env):
    os.environ[env.rate] = '20'
    os.environ[env.seperator] = ';'
    os.environ[env.divider] = ':'
    os.environ[env.default_hours] = '2'
    os.environ[env.prompt] = 'false'
    os.environ[env.allow_empty] = 'false'
    os.environ[env.suppress] = 'false'
    os.environ[env.formula] = 'true'
    os.environ[env.margins] = 'fifty:50;forty:40'
    os.environ[env.discounts] = 'standard:5;deluxe:10;premium:15'
    os.environ[env.deductions] = 'one:100;two:200'

    yield

    clean_env()
