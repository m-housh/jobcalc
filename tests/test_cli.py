#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest
import click
from click.testing import CliRunner

from jobcalc.cli import main
from jobcalc.core import TerminalCalculator


@pytest.fixture()
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(main, ['--help'])
    assert result.exception is None


def test_help_gets_bypassed(runner):
    # if JOBCALC_PROMPT is ``True`` then we invoke the ``prompt-all`` command
    # rather than showing help if no arguments are passed in.
    os.environ['JOBCALC_PROMPT'] = 'true'
    result = runner.invoke(main, input='50\n10\n20\n100\n123 456\n20\n')
    assert '$1,662.20' in result.output
    del(os.environ['JOBCALC_PROMPT'])

    # help get's shown otherwise.
    assert runner.invoke(main).output == runner.invoke(main, ['--help']).output


def test_total(runner):
    result = runner.invoke(main, ['--margin', '50', '--allow-empty', 'total',
                                  '123', '456'],
                           input='\n')
    print(result.exception, result.output)
    assert result.exception is None
    assert '$1,158.00' in result.output

    # hours and rate after the total command
    result = runner.invoke(main, ['--margin', '50', '--discount', '10', 'total',
                                  '--hours', '20', '--rate', '20',
                                  '--deduction', '100', '123', '456'])
    assert result.exception is None
    assert '$1,662.20' in result.output

    # hours and rate before the total command
    result = runner.invoke(main, ['--margin', '50', '--discount', '10',
                                  '--hours', '20', '--rate', '20', 'total',
                                  '--deduction', '100', '123', '456'])
    assert result.exception is None
    assert '$1,662.20' in result.output

    os.environ['JOBCALC_FORMULA'] = 'true'
    result = runner.invoke(main, ['--margin', '50', '--hours', '10', '--rate',
                                  '20', 'total', '123', '456'])
    assert result.exception is None
    assert 'FORMULA' in result.output
    del(os.environ['JOBCALC_FORMULA'])


def test_total_with_prompt(runner):
    # default_hours set in test_env_setup is '2'.
    # rate set in test_env_setup is '20'
    # margins in test_env_setup is 'fifty:50;forty:40'
    # discounts in test_env_setup is 'standard:5;deluxe:10;premium:15'
    # deductions in test_env_setup is 'one:100;two:200'

    # margins input
    result = runner.invoke(main, ['--discount', '10', '--hours', '2', 'total',
                                  '--rate', '20', '--deduction', '100', '123',
                                  '456'],
                           input='50\n')
    assert result.exception is None
    assert '$1,014.20' in result.output


def test_table_no_prompt(runner, test_env_setup):
    # default_hours set in test_env_setup is '2'.
    # rate set in test_env_setup is '20'
    # margins in test_env_setup is 'fifty:50;forty:40'
    # discounts in test_env_setup is 'standard:5;deluxe:10;premium:15'
    # deductions in test_env_setup is 'one:100;two:200'

    # works with ``env_dict`` keys
    result = runner.invoke(main, ['-m', '50', '-d', 'deluxe',
                                  'table', '-r', '20', '-d', '100', '123',
                                  '456'])
    assert result.exception is None
    assert '$1,014.20' in result.output


def test_table_prompt(runner, test_env_setup):
    # default_hours set in test_env_setup is '2'.
    # rate set in test_env_setup is '20'
    # margins in test_env_setup is 'fifty:50;forty:40'
    # discounts in test_env_setup is 'standard:5;deluxe:10;premium:15'
    # deductions in test_env_setup is 'one:100;two:200'

    # rate input
    result = runner.invoke(main, ['--margin', '50', '--discount', 'deluxe',
                                  '--hours', '10', 'table', '--deduction',
                                  '100', '--formula', '123', '456'],
                           input='20')

    assert result.exception is None

    # margins/ hours
    result = runner.invoke(main, ['-d', 'deluxe', 'table', '-d', '100',
                                  '123', '456'],
                           input='50\n20\n')

    assert result.exception is None
    assert '$1,734.20' in result.output

    # costs as inputs
    result = runner.invoke(main, ['-d', 'deluxe', '-m', '50',
                                  '-h', '30', '-r', '20', 'table', '-d', '100'],
                           input='123 456\n')
    assert result.exception is None
    assert '$2,094.20' in result.output

    # discounts as input, also can parse input strings that map to
    # an env_dict
    result = runner.invoke(main, ['-m', '50', '-h', '30', '-r', '20', 'table',
                                  '-d', '100', '123', '456'],
                           input='deluxe\n')
    assert result.exception is None
    assert '$2,094.20' in result.output

    # deductions as an input string.
    result = runner.invoke(main, ['-m', '50', '-d', '10', '-h', '30',
                                  '-r', '20', 'table', '123', '456'],
                           input='50 50\n')
    assert result.exception is None
    assert '$2,094.20' in result.output


def test_table_rate_prompt(runner):
    # rate input
    result = runner.invoke(main, ['--margin', '50', '--discount', '10',
                                  '--hours', '10', 'table', '--deduction',
                                  '100', '123', '456'],
                           input='20\n')
    assert result.exception is None
    assert '$1,302.20' in result.output


def test_formula_no_prompt(runner, test_env_setup):
    # default_hours set in test_env_setup is '2'.
    # rate set in test_env_setup is '20'
    # margins in test_env_setup is 'fifty:50;forty:40'
    # discounts in test_env_setup is 'standard:5;deluxe:10;premium:15'
    # deductions in test_env_setup is 'one:100;two:200'

    result = runner.invoke(main, ['-m', 'fifty', '-d', 'standard', 'formula',
                                  '--table', '--rate', '30', '123', '456'])
    assert result.exception is None
    assert '$1,214.10' in result.output


def test_formula_with_prompt(runner):
    result = runner.invoke(main, ['-m', '50', '-d', '10', '-h', '20',
                                  'formula', '-d', '100', '123', '456'],
                           input='20\n')
    assert result.exception is None
    assert '$1,662.20' in result.output


def test_prompt_all(runner):
    # prompt-all prompt order
    # ('margin', 'discount', 'hours', 'deduction', 'cost', 'rate')
    result = runner.invoke(main, ['prompt-all', '-t', '-f'],
                           input='50\n10\n10 20\n100\n123 456\n20\n')

    assert result.exception is None
    assert '$2,022.20' in result.output
    assert 'DETAILED' in result.output
    assert 'FORMULA' in result.output


def test_TerminalCalc_prompt_for_context_manager(runner):
    @click.command()
    def test_terminal_calc():
        calc = TerminalCalculator()
        # testing that prompt_for works with plural form as well.
        with calc.prompt_for('margins', default='0') as result:
            click.echo(result.value)

    result = runner.invoke(test_terminal_calc, input='20\n')
    assert result.exception is None
    assert "Percentage('0.2')" in result.output


def test_with_config_file(runner, yaml_config):
    result = runner.invoke(main, ['--config', yaml_config, '--margin',
                                  'fifty', '--discount', 'deluxe', 'total',
                                  '--deduction', 'one', '123', '456'])
    assert result.exception is None
    assert "$1,014.20" in result.output
