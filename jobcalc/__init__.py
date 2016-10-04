# -*- coding: utf-8 -*-

# import os
# import logging
# import sys

from .utils import bool_from_env_string, ensure_callback, \
     dict_from_env_string, parse_input_string, flatten, colorize

from .config import Config, TerminalConfig

from .core import Context, PromptResponse, \
    calculate, BaseCalculator, Calculator, TerminalCalculator

from .exceptions import JobCalcError, InvalidEnvString, EnvDictNotFound, \
    NotCallableError, PercentageOutOfRange, NotIterableError, \
    InvalidFormatter, HourlyRateError

from .formatters import BaseFormatter, BasicFormatter, TerminalFormatter, \
    FormulaFormatter


__author__ = 'Michael Housh'
__email__ = 'mhoush@houshhomeenergy.com'
__version__ = '0.1.1'

__all__ = [

    # Utils
    'bool_from_env_string', 'ensure_callback', 'dict_from_env_string',
    'parse_input_string', 'flatten', 'colorize',

    # Config
    # 'ENV_PREFIX', 'CURRENCY_FORMAT', 'LOCALE', 'env_strings',
    'Config', 'TerminalConfig',

    # Core
    'Context', 'PromptResponse',  # 'ColorKey', 'DEFAULT_COLOR_KEY',
    'calculate', 'BaseCalculator', 'Calculator', 'TerminalCalculator',

    # Exceptions
    'JobCalcError', 'InvalidEnvString', 'EnvDictNotFound',
    'NotCallableError', 'PercentageOutOfRange', 'NotIterableError',
    'InvalidFormatter', 'HourlyRateError',

    # Formatters
    # 'ColorContext', 'TotaledContext', 'DEFAULT_COLORS',
    'BaseFormatter', 'BasicFormatter', 'TerminalFormatter', 'FormulaFormatter',

    # Types
    # 'parse_input_value', 'check_env_dict', 'Percentage',
    # 'Currency', 'BaseCurrencyType', 'BasePercentageType', 'DeductionsType',
    # 'MarginsType', 'DiscountsType', 'CostsType', 'HoursType', 'DEDUCTION',
    # 'MARGIN', 'DISCOUNT', 'COSTS', 'HOURS',

    # CLI
    # 'main', 'total', 'table', 'formula', 'prompt_all',

]
