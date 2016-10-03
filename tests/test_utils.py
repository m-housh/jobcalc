#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest
# import decimal

from jobcalc.exceptions import NotCallableError  # , InvalidEnvString
from jobcalc.types import Percentage, DISCOUNT
# from jobcalc.config import ENV_DICT_NAMES as env
from jobcalc.config import Config

from jobcalc.utils import dict_from_env_string, ensure_callback, \
    _return_input, flatten, _converter, parse_input_string, bool_from_env_string


def test_ensure_callback():
    assert ensure_callback(None, error=False) == _return_input
    assert ensure_callback(str) == str
    with pytest.raises(NotCallableError):
        ensure_callback('not callable', error=True)


def test_dict_from_env_string():
    '''
    # fails with no value for a key
    with pytest.raises(InvalidEnvString):
        dict_from_env_string('key1:1.0;key2')
    '''
    with pytest.raises(NotCallableError):
        dict_from_env_string('key1:11;key2:22', type='not callable')

    assert dict_from_env_string('') == {}
    assert dict_from_env_string(None) == {}
    # if we pass in a dict, we short curcuit and return it.
    assert dict_from_env_string({'some': 'dict'}) == {'some': 'dict'}

    parsed_dict = {'key1': '1.0', 'key2': '2.0'}

    envstr = 'key1:1.0;key2:2.0'
    assert dict_from_env_string(envstr) == parsed_dict

    # custom seperator
    envstr = 'key1=1.0;key2=2.0'
    assert dict_from_env_string(envstr, divider='=') == parsed_dict

    # custom seperator in the environment
    os.environ['JOBCALC_DIVIDER'] = '='
    assert dict_from_env_string(envstr) == parsed_dict
    del(os.environ['JOBCALC_DIVIDER'])

    envstr = 'key1:1.0/key2:2.0'
    assert dict_from_env_string(envstr, seperator='/') == parsed_dict
    os.environ['JOBCALC_SEPERATOR'] = '/'
    assert dict_from_env_string(envstr) == parsed_dict
    del(os.environ['JOBCALC_SEPERATOR'])

    # customize the type to convert the values to.
    float_dict = {key: float(value) for (key, value) in
                  zip(parsed_dict.keys(), parsed_dict.values())}

    envstr = 'key1:1.0;key2:2'
    assert dict_from_env_string(envstr, type=float) == float_dict

'''
def test_get_env_var():
    assert get_env_var('invalid', {}) == {}
    assert get_env_var('invalid', default='default') == 'default'
    os.environ['JOBCALC_WITH_PREFIX'] = 'prefix'
    os.environ['NO_PREFIX'] = 'no_prefix'
    os.environ['lower'] = 'lower'
    os.environ['INT'] = '12'

    assert get_env_var('_with_prefix') == 'prefix'
    assert get_env_var('with_prefix') == 'prefix'
    assert get_env_var('WITH_PREFIX') == 'prefix'
    # ensure still works if you have use_prefix ``True`` and the prefix
    # is alread in the string.
    assert get_env_var('JOBCALC_WITH_PREFIX', use_prefix=True) == 'prefix'
    assert get_env_var('with_prefix', ensure_upper=False) == None
    assert get_env_var('with_prefix', use_prefix=False) == None
    assert get_env_var('no_prefix', use_prefix=False) == 'no_prefix'
    assert get_env_var('lower', use_prefix=False, ensure_upper=True) == None
    assert get_env_var('lower', use_prefix=False,
                       ensure_upper=False) == 'lower'

    assert get_env_var('INT', use_prefix=False, callback=int) == 12
    assert isinstance(get_env_var('INT', use_prefix=False, callback=int), int)

    with pytest.raises(TypeError):
        get_env_var('INT', use_prefix=False, callback='not callable')

def test_check_in_env_dict(test_env_setup):

    assert check_in_env_dict('deluxe', env.DISCOUNTS) == '10'
    # should return the value if not in the dict
    assert check_in_env_dict('invalid', env.DISCOUNTS) == 'invalid'
    assert check_in_env_dict('deluxe', env.DISCOUNTS, float) == 10.0

    with pytest.raises(NotCallableError):
        assert check_in_env_dict('deluxe', env.DEDUCTIONS, 'not callable')

    # invalid env dict name returns the value
    assert check_in_env_dict('invalid', 'invalid') == 'invalid'

'''


def test_flatten():
    mylist = [1, 2, [3, 4], [5, [6, 7], [8, 9]]]
    assert list(flatten(mylist)) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # check that ignore types does not flatten, the ignored types
    assert list(flatten(mylist, ignoretypes=(list))) == [mylist]
    assert list(flatten([1, 2, (3, 4, 5)], ignoretypes=tuple)) == \
        [1, 2, (3, 4, 5)]

    assert list(flatten(1)) == [1]
    assert list(flatten(['1', '2', ['3.00', 4, ['5 is alive', [6, 7],
                                                '8', '9']]]
                        )
                ) == ['1', '2', '3.00', 4, '5 is alive', 6, 7,
                      '8', '9']


def test_converter(test_env_setup):
    convert = _converter(DISCOUNT)
    assert convert('deluxe') == Percentage('.1')

    assert convert('standard; deluxe;      premium; 35') == (
        Percentage('0.05'), Percentage('0.1'), Percentage('0.15'),
        Percentage('0.35'))

    with pytest.raises(TypeError):
        _converter(object())


def test_parse_input_string(test_env_setup):
    config = Config()
    assert parse_input_string('123; 456', convert=None) == \
        ('123', '456')

    # can parse a value from and ``env_dict``, if ``convert`` is
    # set properly
    print('config.discounts: {}'.format(config.discounts))
    assert tuple(flatten(
        parse_input_string('12; premium', convert=DISCOUNT))) == \
        (Percentage('.12'), Percentage('.15'))

    # spaces get trimmed
    assert parse_input_string('13;45; 56;    35;10') == \
        ('13', '45', '56', '35', '10')


def test_bool_from_env_string():
    assert bool_from_env_string('true') == True
    assert bool_from_env_string('false') == False
    assert bool_from_env_string('TRUE') == True
    assert bool_from_env_string("FALSE") == False
    assert bool_from_env_string('0') == False
    assert bool_from_env_string('1') == True
    assert bool_from_env_string('3') == False
    assert bool_from_env_string({}) == False
