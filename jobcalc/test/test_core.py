#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import decimal

from jobcalc.types import Currency  # , DISCOUNT  # , Percentage
from jobcalc.exceptions import PercentageOutOfRange, InvalidFormatter, \
    HourlyRateError
from jobcalc.utils import flatten
from jobcalc.formatters import BasicFormatter, FormulaFormatter

from jobcalc.core import calculate, BaseCalculator, Calculator, Context, \
    TerminalCalculator


def test_calculate():
    value = calculate('1234', '50', '10', '300')
    assert isinstance(value, Currency)
    assert value.formatted_string() == '$1,921.20'

    # using decimals as percentages
    assert calculate('1234', '.5', '.1', '300') == value

    with pytest.raises(PercentageOutOfRange):
        calculate('1234', '110', '10', '300')

    with pytest.raises(PercentageOutOfRange):
        calculate('1234', '50', '110', '300')

    assert calculate() == 0


class Test_BaseCalculator(object):

    @classmethod
    def setup_class(cls):
        cls.calc = BaseCalculator(['123', '456'], '50', '10', '100')

    def test_attributes(self):
        assert list(flatten(self.calc.costs)) == ['123', '456']
        assert self.calc.margins == ['50']
        assert self.calc.discounts == ['10']
        assert self.calc.deductions == ['100']

        assert self.calc.total().formatted_string() == '$942.20'

    def test_costs_handle_other_calculators(self):
        calc2 = BaseCalculator(['123', self.calc], '50', '10', '100')
        assert calc2.subtotal() == Currency('1065.2')
        assert calc2.subtotal(ignore_margins=True) == Currency('702')

        # class setting overrides default
        calc2.ignore_margins = True
        assert calc2.subtotal() == Currency('702')

    def test_things_fail_with_invalid_items(self):
        self.calc.costs.append(object())

        with pytest.raises(decimal.InvalidOperation):
            self.calc.total()

        self.calc.costs = self.calc.costs[:-1]
        self.calc.margins.append(object)

        with pytest.raises(decimal.InvalidOperation):
            self.calc.total()

        self.calc.margins = self.calc.margins[:-1]

        self.calc.discounts.append(object())
        with pytest.raises(decimal.InvalidOperation):
            self.calc.total()

        self.calc.discounts = self.calc.discounts[:-1]

        self.calc.deductions.append(object())
        with pytest.raises(decimal.InvalidOperation):
            self.calc.total()

        self.calc.deductions = self.calc.deductions[:-1]


class Test_Calculator(object):

    @classmethod
    def setup_class(cls):
        cls.calc = Calculator(
            costs=['123', '456'],
            margins='50',
            discounts='10',
            deductions='100',
            hours='10',
            rate='20',
            formatters=BasicFormatter
        )

    def test_attributes(self):
        calc = self.calc

        assert isinstance(calc.formatters, list)
        assert calc.formatters[0] == BasicFormatter
        assert calc.rate == decimal.Decimal('20')
        assert calc.hours == ['10']

    def test_render(self):
        assert self.calc.render() == '$1,302.20'

        old_formatters = self.calc.formatters
        self.calc.formatters = []
        assert self.calc.render() == '$1,302.20'

        self.calc.formatters.append([BasicFormatter, BasicFormatter])
        assert self.calc.render() == '$1,302.20\n\n$1,302.20'
        assert self.calc.render('\n\n\n') == '$1,302.20\n\n\n$1,302.20'

        self.calc.formatters = old_formatters

    def test_render_fails_with_invalid_formatter(self):
        old_formatters = self.calc.formatters
        self.calc.formatters = [object()]

        with pytest.raises(InvalidFormatter):
            self.calc.render()

        self.calc.formatters = old_formatters

    def test_ctx_fails_with_strict_option(self):
        old_rate = self.calc.rate
        self.calc.rate = 0
        with pytest.raises(HourlyRateError):
            with self.calc.ctx(strict=True):  # pragma: no cover
                pass

        # doesn't fail if strict is not ``True`` (default).
        with self.calc.ctx() as ctx:
            assert isinstance(ctx, Context)

        self.calc.rate = old_rate

    def test_update(self):
        self.calc.update(
            append=True,
            margins='2.5',
            discounts='5',
            deductions='200',
            hours=('10', '20', '30'),
            rate='30',
            formatters=FormulaFormatter(),
            divider='/',
            prompt=True
        )

        assert self.calc.margins[-1] == '2.5'
        assert self.calc.discounts[-1] == '5'
        assert self.calc.deductions[-1] == '200'
        assert self.calc.hours[-1] == ('10', '20', '30')
        assert self.calc.rate == decimal.Decimal('30')
        assert isinstance(self.calc.formatters[-1], FormulaFormatter)
        assert self.calc.config.divider == '/'

        self.calc.update(
            append=False,
            hours=('20', '10')
        )

        assert self.calc.hours == [('20', '10')]

        class CustomCalc(Calculator):

            def __init__(self, *args, someattr=None, **kwargs):
                super().__init__(*args, **kwargs)
                self.someattr = someattr

        calc = CustomCalc(someattr='a')
        assert calc.someattr == 'a'
        calc.update(
            append=True,
            someattr='somevalue'
        )
        assert calc.someattr == 'somevalue'

    def test_rate_does_not_change_with_invalid(self):
        self.calc.rate = decimal.Decimal('20')
        assert self.calc.rate == decimal.Decimal('20')
        self.calc.rate = None
        assert self.calc.rate == decimal.Decimal('20')
        self.calc.rate = '-1'
        assert self.calc.rate == decimal.Decimal('20')


def test_TerminalCalculator_prompt_for_fails():
    calc = TerminalCalculator()
    with pytest.raises(AttributeError):
        calc._prompt_for('invalid')


def test_TerminalCalculator_key_for_prompt():
    calc = TerminalCalculator()
    # check all the prompts.
    for prompt in calc._prompts:
        if prompt == 'rate' or prompt == 'hours':
            assert calc.key_for_prompt(prompt) == prompt
        else:
            assert calc.key_for_prompt(prompt) == prompt + 's'

    # we can also handle if someone accidentally asks to prompt for a plural
    # version, without raising errors.
    assert calc.key_for_prompt('margins') == 'margins'

    # fail with invalid prompt.
    with pytest.raises(AttributeError):
        calc.key_for_prompt('invalid')


def test_TerminalCalculator_prompt_for_context_manager_fails():
    calc = TerminalCalculator()
    with pytest.raises(AttributeError):
        with calc.prompt_for('invalid'):  # pragma: no cover
            pass
