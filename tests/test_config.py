#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from jobcalc.config import Config, TerminalConfig, env_strings


def test_env_strings():
    assert env_strings.seperator == 'JOBCALC_SEPERATOR'
    assert env_strings.divider == 'JOBCALC_DIVIDER'
    assert env_strings.rate == 'JOBCALC_RATE'
    assert env_strings.default_hours == 'JOBCALC_DEFAULT_HOURS'
    assert env_strings.margins == 'JOBCALC_MARGINS'
    assert env_strings.discounts == 'JOBCALC_DISCOUNTS'
    assert env_strings.deductions == 'JOBCALC_DEDUCTIONS'
    assert env_strings.prompt == 'JOBCALC_PROMPT'
    assert env_strings.allow_empty == 'JOBCALC_ALLOW_EMPTY'
    assert env_strings.suppress == 'JOBCALC_SUPPRESS'
    assert env_strings.formula == 'JOBCALC_FORMULA'


def test_Config(test_env_setup):
    config = Config()
    assert config.debug is True
    assert config.seperator == ';'
    assert config.divider == ':'
    assert config.rate == '20'
    assert config.default_hours == '2'
    assert config.margins == {'fifty': '50', 'forty': '40'}
    assert config.discounts == {'standard': '5', 'deluxe': '10',
                                'premium': '15'}
    assert config.deductions == {'one': '100', 'two': '200'}

    # test if variable is set to an empty string we return the default
    os.environ['JOBCALC_RATE'] = ''
    config = Config()
    assert config.rate == '0'


def test_Config_defaults():
    config = Config()
    assert config.seperator == ';'
    assert config.divider == ':'
    assert config.rate == '0'
    assert config.default_hours == '0'
    assert config.margins == {}
    assert config.discounts == {}
    assert config.deductions == {}


def test_TerminalConfig(test_env_setup):
    config = TerminalConfig()
    assert config.allow_empty is False
    assert config.formula is True
    assert config.suppress is False
    assert config.prompt is False
