#!/usr/bin/env python
# -*- coding: utf-8 -*-

import decimal

import pytest
import terminaltables

from jobcalc.core import BaseCalculator, Calculator
from jobcalc.utils import colorize

from jobcalc.formatters import BaseFormatter, BasicFormatter, \
    TerminalFormatter, FormulaFormatter, DEFAULT_FORMULA_STRING, \
    TotaledContext, DEFAULT_COLORS


@pytest.fixture()
def calculator():
    return Calculator(
        costs=['123', '456'],
        margins='50',
        discounts='10',
        deductions='100',
        hours='10',
        rate='20'
    )


def test_BaseFormatter():
    with pytest.raises(NotImplementedError):
        BaseFormatter.render(None)


def test_BasicFormatter():

    with pytest.raises(TypeError):
        BasicFormatter.render(object())

    calc = BaseCalculator(['123', '456'], '50', '10', '100')
    assert BasicFormatter.render(calc) == '$942.20'


def test_TerminalFormatter():
    calc = Calculator(
        costs=['123', '456'],
        margins='50',
        discounts='10',
        deductions='100',
        hours='10',
        rate='20',
        formatters=TerminalFormatter()
    )

    table_data = [
        ['SUBTOTAL', 'MARGIN', 'DISCOUNT', 'DEDUCTION', 'TOTAL'],
        [
            colorize('$779.00', 'magenta'),
            colorize('50.0%', 'blue'),
            colorize('10.0%', 'yellow'),
            colorize('$100.00', 'red'),
            colorize('$1,302.20', 'green')
        ]
    ]

    table = terminaltables.AsciiTable(table_data, title='DETAILED')

    assert calc.render() == table.table

    # costimized colors and title
    calc2 = Calculator(
        costs=['123', '456'],
        margins='50',
        discounts='10',
        deductions='100',
        hours='10',
        rate='20',
        formatters=TerminalFormatter('yellow', 'magenta', 'red', 'green',
                                     'blue', title='SOMETHING')
    )

    table_data[1] = [
            colorize('$779.00', 'yellow'),
            colorize('50.0%', 'magenta'),
            colorize('10.0%', 'red'),
            colorize('$100.00', 'green'),
            colorize('$1,302.20', 'blue')
        ]
    table2 = terminaltables.AsciiTable(table_data, title='SOMETHING')
    assert calc2.render() == table2.table

    # colorize the headers too.
    table2.table_data[0] = list(map(lambda x: TerminalFormatter.colorize(*x),
                                    zip(table2.table_data[0],
                                        ('yellow', 'magenta', 'red', 'green',
                                         'blue'))))

    calc2.formatters[0].color_header = True
    assert calc2.render() == table2.table


def test_FormulaFormatter(calculator):
    formatter = FormulaFormatter(no_color=True)
    calculator.formatters = [formatter]

    with calculator.ctx() as ctx:
        values = TotaledContext(
            *map(lambda x: x.formatted_string(),
                 list(ctx) + [calculator.total()]))._asdict()

        values['header'] = ' '.join(('subtotal', 'margin', 'discount',
                                     'deduction', 'total'))
        hours = calculator._hours()
        rate = decimal.Decimal(calculator.rate)
        values['subtotal_string'] = \
            'subtotal = ({costs} + ({hours} * {rate}))'.format(
                costs=ctx.subtotal - (hours * rate),
                hours=hours,
                rate=rate)

        string = DEFAULT_FORMULA_STRING.format(**values)

        assert calculator.render() == 'FORMULA\n' + '-------\n' + string

        # custom colors
        colors = ('red', 'blue', 'yellow', 'green', 'magenta')
        formatter = FormulaFormatter(*colors)
        calculator.formatters = [formatter]
        values2 = TotaledContext(*map(lambda x: formatter.colorize(*x),
                                      zip(list(ctx) + [calculator.total()],
                                          colors)))._asdict()
        values2['header'] = ' '.join(map(lambda x: formatter.colorize(*x),
                                         zip(values['header'].split(),
                                             colors)))
        values2['subtotal_string'] = values['subtotal_string']

        string2 = DEFAULT_FORMULA_STRING.format(**values2)
        assert calculator.render() == 'FORMULA\n' + '-------\n' + string2

        # custom formula string
        custom_string = """
        {subtotal_string}
        {header}
        {subtotal}\t{margin}\t{discount}\t{deduction}
        """

        formatter = FormulaFormatter(*colors, formula_string=custom_string)
        calculator.formatters = [formatter]
        string3 = custom_string.format(**values2)
        assert calculator.render() == 'FORMULA\n' + '-------\n' + string3

        formatter = FormulaFormatter()
        assert formatter.colors == DEFAULT_COLORS
