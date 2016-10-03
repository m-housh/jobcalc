#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest
import decimal

import click

from jobcalc.param_types import Percentage, Currency, DeductionsType, \
    MarginsType, DiscountsType, CostsType, check_env_dict, parse_input_value, \
    HoursType, ConfigType

from jobcalc.exceptions import PercentageOutOfRange, EnvDictNotFound
from jobcalc.config import env_strings as env


def test_parse_input_value():

    @parse_input_value
    def works(values):
        return values

    assert works('123;456') == ('123', '456')
    assert works('123') == ('123', )


def test_check_env_dict(test_env_setup):

    # fails if strict is true and an ``env_dict`` is not found.
    with pytest.raises(EnvDictNotFound):
        @check_env_dict('JOBCALC_INVALID_VAR_NAME', strict=True)
        def invalid_decorated(values):  # pragma: no cover
            pass

        invalid_decorated()

    # works if ``strict`` is not True.
    @check_env_dict("JOBCALC_INVALID_VAR_NAME", strict=False)
    def works(values):
        return values

    assert works(('123', '456')) == ('123', '456')

    # same if default's ``strict`` being ``False``, and ``env_var`` being
    # ``None``
    @check_env_dict()
    def works(values):
        return values

    assert works(('123', '456')) == ('123', '456')

    # fails if strict is true and an ``env_var`` is not ``None``.
    with pytest.raises(EnvDictNotFound):
        @check_env_dict(None, strict=True)
        def invalid_decorated(values):  # pragma: no cover
            pass

        invalid_decorated()

    os.environ['JOBCALC_DISCOUNTS'] = \
        'standard:5;deluxe:10;premium:15;default:deluxe'

    # test with a single value.
    @check_env_dict(env.discounts)
    def works(value):
        return value

    assert works('deluxe') == '10'
    assert works(('standard', 'deluxe', 'premium')) == ('5', '10', '15')
    assert works('0') == '10'


def test_Percentage():
    assert Percentage('.10').formatted_string() == '10.0%'
    assert isinstance(Percentage('10'), decimal.Decimal)
    assert Percentage('10').formatted_string() == '10.0%'
    assert repr(Percentage(10)) == "Percentage('0.1')"
    assert Percentage(Percentage('10') + Percentage('5')
                      ).formatted_string() == '15.0%'

    with pytest.raises(PercentageOutOfRange):
        Percentage('110')

    # we can also convert a formatted string (ex. '10.0%') to a ``Percentage``.
    assert Percentage(
        Percentage('10').formatted_string()).formatted_string() == '10.0%'

    with pytest.raises(decimal.InvalidOperation):
        Percentage(object())


def test_Dollars():
    assert Currency('10000.03').formatted_string() == '$10,000.03'
    assert Currency('10000.036').formatted_string() == '$10,000.04'
    assert Currency('-12345').formatted_string() == '$12,345.00'
    assert repr(Currency('1')) == "Currency('1')"

    # we can also convert a formatted_string
    assert Currency(
        Currency('100').formatted_string()).formatted_string() == '$100.00'

    with pytest.raises(decimal.InvalidOperation):
        Currency(object())


def test_DeductionsType(test_env_setup):
    deductions = DeductionsType()
    values = [('one', '$100.00'), ('two', '$200.00')]
    for key, value in values:
        assert deductions.convert(key, None, None
                                  ).formatted_string() == value
        assert isinstance(deductions.convert(key, None, None), Currency)

    assert deductions.convert('1000.3000005', None,
                              None).formatted_string() == '$1,000.30'


def test_MarginsType(test_env_setup):
    margins = MarginsType()
    assert isinstance(margins, click.ParamType)
    # value retrieved from the environment dict.
    value = margins.convert('fifty', None, None)
    assert isinstance(value, Percentage)
    assert value.formatted_string() == '50.0%'
    assert float(value) == 0.50

    # percentages can not exceed 100
    with pytest.raises(click.BadParameter):
        margins.convert('110', None, None)

    # fails if any one of a list fails.
    with pytest.raises(click.BadParameter):
        margins.convert('10;20;111', None, None)

    # value not in the environment dict.
    assert margins.convert('99.99', None, None).formatted_string() == \
        '99.9%'


def test_DiscountsType(test_env_setup):
    discounts = DiscountsType()
    values = [('standard', '5.0%'), ('deluxe', '10.0%'), ('premium', '15.0%')]
    for key, value in values:
        assert discounts.convert(key, None, None).formatted_string() == value
        assert isinstance(discounts.convert(key, None, None), Percentage)

    assert float(discounts.convert('35', None, None)) == 0.35

    with pytest.raises(click.BadParameter):
        discounts.convert('110', None, None)


def test_CostsType():
    costs = CostsType()
    assert costs.convert('123;456', None, None) == \
        (Currency('123'), Currency('456'))

    assert costs.convert('123', None, None) == Currency('123')


def test_HoursType():
    hours = HoursType()
    assert hours.convert('10;20', None, None) == \
        (decimal.Decimal('10'), decimal.Decimal('20'))
    assert hours.convert('20', None, None) == decimal.Decimal('20')


def test_ConfigType():
    config = ConfigType()
    with pytest.raises(click.BadParameter):
        config.convert('/invalid/path', None, None)
