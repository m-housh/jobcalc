# -*- coding: utf-8 -*-

from typing import Dict, Optional
import os
import logging
from collections import namedtuple

from .utils import dict_from_env_string, bool_from_env_string
from . import debug as DEBUG

logger = logging.getLogger(__name__)

ENV_PREFIX = 'JOBCALC'
"""The prefix to use for all environment variables."""

CURRENCY_FORMAT = os.environ.get(ENV_PREFIX + '_CURRENCY_FORMAT', 'USD')
"""The currency format to use when formatting a currency string.  Should be
a valid format used by ``babel.numbers.format_currency``.

This can be set by the ``JOBCALC_CURRENCY_FORMAT`` environment variable.
Defaults to ``'USD'``.

"""

LOCALE = os.environ.get(ENV_PREFIX + '_LOCALE', 'en_US')
"""The default locale to set for formatting a currency string.  Should be a
valid locale used by ``babel.numbers.format_currency``.

This can be set by the ``JOBCALC_CURRENCY_FORMAT`` environment variable.
Defaults to ``'en_US'``.

"""


_EnvStrings = namedtuple('_EnvStrings', ('seperator', 'divider', 'rate',
                                         'default_hours', 'margins',
                                         'discounts', 'deductions', 'prompt',
                                         'allow_empty', 'suppress', 'formula',
                                         'prompt_seperator'
                                         )
                         )

env_strings = _EnvStrings(*map(lambda x: ENV_PREFIX + '_' + x.upper(),
                               _EnvStrings._fields))
"""A named tuple that holds all the commonly used environment variables.
Primarily used to avoid typo's and make an IDE work better.
"""


class Config(object):
    """The main config class that holds common varibles that are used
    to set up a calculator instance.  These variables can either be passed in
    or retrieved from their corresponding environment variable.

    :param seperator:  A seperator used to seperate key, value pairs parsed
                       from an environment variable.  Defaults to ``';'``.
                       Can be set by ``JOBCALC_SEPERATOR``.  (ex.
                       'key1:value1;key2:value2;')
    :param divider:  Used to divide a key, value pair parsed from an environment
                     variable.  Defaults to ``':'``.  Can be set by
                     ``JOBCALC_DIVIDER``. (ex. 'key1:value1')
    :param rate:  An hourly rate to be used in calculations.  Defaults to '0'.
                  Can be set by ``JOBCALC_RATE``.
    :param default_hours:  Hours to ``always`` be used for a calculation.
                           Defaults to ``'0'``.  Can be set by
                           ``JOBCALC_DEFAULT_HOURS``.
    :param margins:  A dict with named margins that can be used in a
                     calculation.  Defaults to ``{}``.  Can be set by
                     ``JOBCALC_MARGINS`` using the ``seperator`` and ``divider``
                     to distinguish the key, value pairs.  All values will get
                     converted to a ``Percentage`` to be used as a profit
                     margin. (ex: 'fifty:50;forty:40').
    :param discounts:  A dict with named discounts that can be used in a
                       calculation.  Defaults to ``{}``.  Can be set by
                       ``JOBCALC_DISCOUNTS`` using the ``seperator`` and
                       ``divider`` to distinguish the key, value pairs.  All
                       values will get converted to a ``Percentage`` to be used
                       as a percentage discount.
                       (ex. 'standard:10;deluxe:15').
    :param deductions:  A dict with named deductions that can be used in a
                        calculation.  Defaults to ``{}``.  Can be set by
                        ``JOBCALC_DEDUCTIONS`` using the ``seperator`` and
                        ``divider`` to distinguish key, value pairs.  All
                        values will get converted to a ``Currency`` to be used
                        as a monetary deduction. (ex. 'one:100;two:200')
    :param debug:  A bool to put calculator into debug mode.  Defaults to
                   ``False``.

    """

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
    """Extends ``Config`` with command line interface specific variables.

    .. note::

        Boolean envrionment variable's will be determined as ``True`` with
        any of the following values.  Anything else is ``False``.

        * 'True'
        * 'TrUe'  (any combination upper-lower works)
        * '1'

    :param prompt:  A bool that if ``True`` will call the ``prompt-all``
                    sub-command if the main (``job-calc``) command is called
                    without a sub-command.  If ``False`` then we show the
                    help doc.  Default is ``False``.  Can be set by
                    ``JOBCALC_PROMPT``.
    :param suppress:  A bool that if ``True`` will suppress the detailed
                      table output for any commands called.  Default is
                      ``False``.  Can be set by ``JOBCALC_SUPPRESS``.
    :param formula:  A bool that if ``True`` will show the formula string for
                     any commands called.  Default is ``False``. Can be set
                     by ``JOBCALC_FORMULA``.
    :param allow_empty:  A bool that if ``True`` will not prompt for empty
                         values before performing any calculations.  Can be
                         set by ``JOBCALC_ALLOW_EMPTY``.
    :param prompt_seperator:  A string that is used to seperate items that can
                              be multiple values if prompted for.  Defaults to
                              ``' '``.  Can be set by
                              ``JOBCALC_PROMPT_SEPERATOR``.

    """
    def __init__(self, *, prompt: bool=None, suppress: bool=None,
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
