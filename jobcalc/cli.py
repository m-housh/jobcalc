#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import os
import logging

import click

from . import param_types as types
from .core import TerminalCalculator
from .formatters import FormulaFormatter, TerminalFormatter, BasicFormatter
from .config import ENV_PREFIX, TerminalConfig

logger = logging.getLogger(__name__)


# TODO: Add a way to turn colors off.
#       Remove suppress, from here and config.
@click.group(no_args_is_help=False, invoke_without_command=True)
@click.option('-m', '--margin', default='0', type=types.MARGIN,
              help='A percent to use for the profit margin')
@click.option('-d', '--discount', default='0', type=types.DISCOUNT,
              help='A percentage discount to apply')
@click.option('-h', '--hours', default='0', type=types.HOURS,
              help='Amount of hours for the job')
@click.option('-r', '--rate', default=0, type=int,
              help='An hourly rate to use in the calculation.')
@click.option('-a', '--allow-empty', is_flag=True, default=False,
              envvar=ENV_PREFIX + '_ALLOW_EMPTY',
              help='Option to prompt for empty values.')
@click.option('-c', '--config', type=types.CONFIG, is_eager=True,
              envvar=ENV_PREFIX + '_CONFIG', nargs=1,
              help='Path to a config file for the calculator')
@click.pass_context
def main(ctx, margin, discount, rate, hours, allow_empty, config):
    """Calculate a job cost based on the settings.

    OPTIONS:

    MARGIN, DISCOUNT, and ALLOW_EMPTY  should be set before the COMMAND,
    optionally setting HOURS and RATE.

    DEDUCTION (a monetary discount), HOURS, and RATE can be set
    after the COMMAND.

    COSTS:
    Are all ARGS after the COMMAND and after all OPTIONS for the command

    SUBCOMMAND-HELP:
    For info on a particular COMMAND and it's OPTIONS

    job-calc COMMAND --help


    """

    if config is None:
        # setup our config object.
        config = TerminalConfig(
            rate=rate,
            allow_empty=allow_empty
        )

    if ctx.invoked_subcommand is None and config.prompt is False:
        click.echo(ctx.get_help())
    else:
        calculator = TerminalCalculator(
            margins=margin,
            discounts=discount,
            hours=hours,
            config=config
        )

        # set calculator as the ctx.obj
        ctx.obj = calculator

        logger.debug('config.formula: {}'.format(config.formula))

    if ctx.invoked_subcommand is None and config.prompt is True:
        # setup our calculator object to pass to the prompt_all command.
        ctx.invoke(prompt_all)


@main.command()
@click.option('-d', '--deduction', default='0', type=types.DEDUCTION,
              help='A monetary discount to subtract from the total')
@click.option('-h', '--hours', default='0', type=types.HOURS,
              help='Amount of hours for the job')
@click.option('-r', '--rate', default=0, type=int,
              help='An hourly rate to use in the calculation.')
@click.argument('costs', nargs=-1, type=types.COSTS)
@click.pass_obj
def total(calculator, deduction, hours, rate, costs):
    """Shows the monetary total only for the calculation."""
    calculator.update(
        append=True,
        costs=costs,
        deductions=deduction,
        hours=hours,
    )

    if rate != 0:
        calculator.rate = rate

    if calculator.config.allow_empty is False:
        calculator.prompt_for_empty()
        click.echo('\n\n')

    if calculator.config.formula is True:
        calculator.formatters.append(FormulaFormatter())

    calculator.formatters.append(BasicFormatter())

    # default formatter just shows the total.
    click.echo(calculator.render())


@main.command()
@click.option('-f', '--formula', is_flag=True, default=False,
              help='Show the formula as well.')
@click.option('-d', '--deduction', default='0', type=types.DEDUCTION,
              help='A monetary discount to subtract from the total')
@click.option('-h', '--hours', default='0', type=types.HOURS,
              help='Amount of hours for the job')
@click.option('-r', '--rate', default=0, type=int,
              help='An hourly rate to use in the calculation.')
@click.argument('costs', nargs=-1, type=types.COSTS)
@click.pass_obj
def table(calculator, formula, deduction, hours, rate, costs):
    """Shows a detailed table view of the calculation."""

    calculator.update(
        append=True,
        costs=costs,
        deductions=deduction,
        hours=hours,
    )

    if rate != 0:
        calculator.rate = rate

    config = calculator.config
    if formula is True:
        config.formula = formula

    if config.allow_empty is False:
        # prompt for the values that are equal to 0
        # TODO:  Add ability to pass ``strict`` parameter to
        #        ``prompt_for_empty``
        calculator.prompt_for_empty()

    calculator.formatters.append(TerminalFormatter())

    if config.formula is True:
        calculator.formatters.append(FormulaFormatter())

    click.echo('\n\n' + calculator.render())


@main.command()
@click.option('-d', '--deduction', default='0', type=types.DEDUCTION,
              help='A monetary discount to subtract from the total')
@click.option('-h', '--hours', default='0', type=types.HOURS,
              help='Amount of hours for the job')
@click.option('-r', '--rate', default=0, type=int,
              help='An hourly rate to use in the calculation.')
@click.option('-t', '--table', is_flag=True, default=False,
              help='Show the detail table as well')
@click.argument('costs', nargs=-1, type=types.COSTS)
@click.pass_obj
def formula(calculator, deduction, hours, rate, table, costs):
    """Shows a formula view of the calculation."""

    calculator.update(
        costs=costs,
        deductions=deduction,
        hours=hours,
    )

    if rate != 0:
        calculator.rate = rate

    calculator.formatters.append(FormulaFormatter())

    if table is True:
        calculator.formatters.append(TerminalFormatter())

    if calculator.config.allow_empty is False:
        calculator.prompt_for_empty()

    click.echo('\n\n' + calculator.render())


@main.command('prompt-all')
@click.option('-t', '--table', is_flag=True, default=False,
              help='Show the detail table')
@click.option('-f', '--formula', is_flag=True, default=False,
              help='Show the formula')
@click.pass_obj
def prompt_all(calculator, table, formula):
    """Prompt's for all values for the calculation."""

    calculator.prompt_all()

    if table is True:
        calculator.formatters.append(TerminalFormatter())

    if formula is True or calculator.config.formula is True:
        calculator.formatters.append(FormulaFormatter())

    click.echo('\n\n')
    click.echo(calculator.render())


if __name__ == '__main__':  # pragma: no cover
    main(auto_envvar_prefix=ENV_PREFIX)
