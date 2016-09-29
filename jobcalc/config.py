# -*- coding: utf-8 -*-

from typing import Dict, Optional
import os
import logging
from collections import namedtuple

from .utils import dict_from_env_string, bool_from_env_string
from . import debug as DEBUG

logger = logging.getLogger(__name__)

ENV_PREFIX = 'JOBCALC'

CURRENCY_FORMAT = os.environ.get(ENV_PREFIX + '_CURRENCY_FORMAT', 'USD')
LOCALE = os.environ.get(ENV_PREFIX + '_LOCALE', 'en_US')

EnvStrings = namedtuple('EnvStrings', ('seperator', 'divider', 'rate',
                                       'default_hours', 'margins', 'discounts',
                                       'deductions', 'prompt', 'allow_empty',
                                       'suppress', 'formula', 'prompt_seperator'
                                       ))

env_strings = EnvStrings(*map(lambda x: ENV_PREFIX + '_' + x.upper(),
                              EnvStrings._fields))


class Config(object):

    def __init__(self, *, seperator: str=None, divider: str=None,
                 rate: str=None, default_hours: str=None,
                 margins: Dict[str, str]=None, discounts: Dict[str, str]=None,
                 deductions: Dict[str, str]=None, debug: bool=None
                 ) -> None:

        self.debug = bool(debug) if debug is not None else DEBUG

        # Used to seperate items in a string.
        # Example: '123;456' would parse to ('123', '456')
        self.seperator = str(seperator) if seperator else \
            self._get(env_strings.seperator, ';')

        # Used to divide key, value pairs in a string.
        # Example: 'key1:value' would parse to {'key1': 'value1'}
        self.divider = str(divider) if divider else \
            self._get(env_strings.divider, ':')

        # An hourly rate to use in calculations.
        self.rate = str(rate) if rate else \
            self._get(env_strings.rate, '0')

        # Default hours to use in calculations.
        # these are hours that should be used in every calculation, for example
        # if there is are a minimum number of hours to charge for.
        self.default_hours = str(default_hours) if default_hours else \
            self._get(env_strings.default_hours, '0')

        self.margins = dict(margins) if margins else \
            self._env_dict(env_strings.margins)

        self.discounts = dict(discounts) if discounts else \
            self._env_dict(env_strings.discounts)

        self.deductions = dict(deductions) if deductions else \
            self._env_dict(env_strings.deductions)

    def _get(self, key: str, default: Optional[str]) -> str:
        """Ensures that if an env var is set to an empty string ('') we return
        the default value.
        """
        var = os.environ.get(key, default)
        if var == '':
            return default
        return var

    def _env_dict(self, key: str) -> Dict[str, str]:
        """Helper to return a dict from an env string key. """
        return dict_from_env_string(
            os.environ.get(key),
            seperator=self.seperator,
            divider=self.divider
        )


class TerminalConfig(Config):

    def __init__(self, prompt: bool=None, suppress: bool=None,
                 formula: bool=None, allow_empty: bool=None,
                 prompt_seperator: str=None, **kwargs
                 ) -> None:

        super().__init__(**kwargs)

        # whether to prompt for values or not.
        self.prompt = bool(prompt) if prompt else \
            self._bool_from(env_strings.prompt, False)

        # seperator to use for prompts that accept multiple values.
        # default is ' '
        self.prompt_seperator = str(prompt_seperator) if prompt_seperator else \
            self._get(env_strings.prompt_seperator, ' ')

        # allow empty values.
        self.allow_empty = bool(allow_empty) if allow_empty else \
            self._bool_from(env_strings.allow_empty, False)

        # suppress detailed table output.
        self.suppress = bool(suppress) if suppress else \
            self._bool_from(env_strings.suppress, False)

        # show the formula string.
        self.formula = bool(formula) if formula else \
            self._bool_from(env_strings.formula, False)

    def _bool_from(self, key: str, default: bool) -> bool:
        value = self._get(key, None)
        if value is None:
            return default
        return bool_from_env_string(value)
