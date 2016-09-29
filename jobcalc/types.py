# -*- coding: utf-8 -*-

from typing import Any, Tuple, Union
import decimal
import logging

import click
import wrapt
import babel.numbers

from .utils import parse_input_string
from .exceptions import PercentageOutOfRange, EnvDictNotFound
from .config import Config, env_strings, CURRENCY_FORMAT, LOCALE

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@wrapt.decorator
def parse_input_value(wrapped, instance, args, kwargs):
    """A decorator to parse the first arg with ``parse_input_string``, before
    sending on to the wrapped function/method.

    Works properly with methods attached to classes or stand alone functions.

    :Example:

        >>> @parse_input_value
        ... def decorated(values):
        ...    print(values)
        >>> decorated('123;456;')
        ('123', '456')

        >>> class Parsed(object):
        ...    @parse_input_value
        ...    def decorated(self, values):
        ...        print(values)
        >>> Parsed().decorated('123;456')
        ('123', '456')


    .. note::

        This method uses ``parse_input_string`` method which always returns
        a tuple, so the parsed value that get's passed to the wrapped method
        will always be a tuple, which can be of length 1, if there wasn't any
        values to split in the input string.

        :Example:

            >>> @parse_input_value
            ... def decorated(value):
            ...   print(value)
            >>> decorated('123')
            ('123', )


    """
    values = parse_input_string(args[0])
    newargs = (values,) + args[1:]
    return wrapped(*newargs, **kwargs)


def check_env_dict(env_var: str=None, strict: bool=None):
    """A decorator to check iterate over the first arg, checking if the values
    map to a key in an ``env_dict``, returning it's value if so. Parsing the
    first arg to a true value. (either the value for the ``env_dict`` key or
    the value itself, if not a key in the ``env_dict``.

    This will work the same whether wrapping a method attached to a class or
    a stand alone function.


    :param env_var:  The name of the ``env_dict`` to check in.
    :param strict:  A bool, if ``True`` then an error will be raised if an
                    ``env_dict`` is not found for ``env_var``.  Default is
                    ``None`` (``False``).

    :raises EnvDictNotFound:  If ``strict`` is ``True`` and an ``env_dict``
                              was not found for ``env_var``.


    :Example:

        ```
        $ export JOBCALC_DISCOUNTS='standard:5;deluxe:10;premium:15'
        ```

        ```
        >>> @check_env_dict('JOBCALC_DISCOUNTS')
        ... def decorated(value):
        ...    print(value)
        >>> decorated('standard')
        '5'
        >>> decorated('not_in_dict')
        'not_in_dict'


    """
    @wrapt.decorator
    def check_env_dict_wrapper(wrapped, instance, args, kwargs):
        logger.debug('args: {}'.format(args))

        # use ``env_var`` if set, or check instance for an attribute
        # ``env_dict_name``.
        env_name = env_var or getattr(instance, 'env_dict_name', None)

        # check if the env_name is in env_strings helper
        # if so, we need to actually get the key.
        if env_name in env_strings:
            for key, value in env_strings._asdict().items():
                if value == env_name:
                    env_name = key

        is_strict = strict or getattr(instance, 'error_if_not_found', None)

        # config holds the env dict's to search in for the key.
        config = Config()

        logger.debug('checking config for env_name: {}'.format(env_name))

        # get the env dict, parsed using ``parse_env_string``, or
        # return an empty dict.
        if env_name is None:
            env_dict = {}
        else:
            env_dict = getattr(config, env_name, {})
        # env_dict = parse_env_string(os.environ.get(env_name, {}))
        # short curcuit if we don't have an env name to search for.
        if env_dict == {}:
            logger.debug('No env dict found for: {}'.format(
                env_name)
            )
            if is_strict is True:
                raise EnvDictNotFound(env_name)
            return wrapped(*args, **kwargs)

        if isinstance(args[0], str):
            # if only a single value was passed in
            return env_dict.get(args[0], args[0])

        # if multiple values need to be checked, a list, tuple, etc.
        # check for the values, either returning the value for the key in the
        # env_dict, or the value.
        true_values = tuple(map(lambda x: env_dict.get(x, x), iter(args[0])))

        # if only parsed a single item, return a single item,
        # instead of a tuple
        if len(true_values) == 1:
            true_values = true_values[0]

        # reset args, to be passed along.
        newargs = (true_values,) + args[1:]

        # call the wrapped method
        return wrapped(*newargs, **kwargs)

    return check_env_dict_wrapper


class Percentage(decimal.Decimal):
    """A ``Decimal`` sub-class, that handle's percentages correctly for
    our app.  Adds a ``formatted_string`` method for a percentage.

    A percentage for our purposes can either be a number between 0 and
    100.  If the number is between 0 and 1, then it is used as the percentage.
    If it is above 1 and less than 100, we divide the number by 100 to create
    or percentage.


    :raises PercentageOutOfRange:  If the value is a negative number or
                                   100 or above.


    .. note::

        When performing any operations (like addition, multiplication, etc.) to
        a ``Percentage``, then the new value will need to be converted back
        to a ``Percentage`` for the ``formatted_string`` method to
        work.

        :Example:

            >>> p = Percentage('10')
            >>> repr(p)
            "Percentage('0.1')"
            >>> x = Percentage('10') + Percentage('5')
            >>> repr(x)
            "Decimal('0.15')"
            >>> x.formatted_string()
            Traceback ...
            AttributeError: 'decimal.Decimal' object has no attribute
            'formatted_string'

            >>> x = Percentage(Percentage('10') + Percentage('5'))
            >>> x.formatted_string()
            '15.0%'

    :10% Example:

        >>> Percentage('10').formatted_string()
        '10.0%'
        >>> Percentage('.1').formatted_string()
        '10.0%'
        >>> Percentage(
        ...    Percentage('10').formatted_string()).formatted_string())
        '10.0%'

    """

    def __new__(cls, value: Any) -> 'Percentage':
        try:
            value = decimal.Decimal(str(value))
        except decimal.InvalidOperation:
            # handles if someone passes a ``formatted_string``,
            # then we will try to get the value from that as well.
            try:
                value = decimal.Decimal(''.join(str(value).split('%')))
            except decimal.InvalidOperation as exc:
                # all our options failed trying to parse the value to
                # a Decimal
                raise exc

        # check the value if it's between 0 and 1, then pass it
        # along.
        if 0 <= value < 1:
            return decimal.Decimal.__new__(cls, str(value))
        elif 1 <= value < 100:
            # if the value is between 1 and 100, then we divide it
            # by 100 to get the proper decimal value.
            return decimal.Decimal.__new__(cls,
                                           str(value / 100))
        else:
            # raise an error
            raise PercentageOutOfRange(value)

    def formatted_string(self) -> str:
        return '{:.1f}%'.format(
            (self * 100).quantize(decimal.Decimal('.1'),
                                  rounding=decimal.ROUND_DOWN))

    def __repr__(self) -> str:
        return "{}('{}')".format(self.__class__.__name__, str(self))


class Currency(decimal.Decimal):
    """A ``Decimal`` sub-class that knows how to handle currency for our app.
    Adds a ``formatted_string`` method to represent a currency instance.

    ``Currency`` will convert any negative numbers to a positive number, which
    is what is required by our calculations.

    .. note::

        When performing any operations (like addition, multiplication, etc.) to
        a ``Currency``, then the new value will need to be converted back
        to a ``Currency`` for the ``formatted_string`` method to
        work.

    """

    def __new__(cls, value: Any) -> 'Currency':
        try:
            value = decimal.Decimal(str(value))
        except decimal.InvalidOperation:
            # handles if a formatted_string is passed in.
            try:
                symbol = babel.numbers.get_currency_symbol(CURRENCY_FORMAT,
                                                           locale=LOCALE)
                value = decimal.Decimal(''.join(str(value).split(symbol)))
            except (decimal.InvalidOperation) as exc:
                # we tried all we can, so raise the exception
                raise exc

        # ensure positive numbers only
        if value < 0:
            return decimal.Decimal.__new__(cls, str(value * -1))
        return decimal.Decimal.__new__(cls, str(value))

    def formatted_string(self) -> str:
        return babel.numbers.format_currency(self, CURRENCY_FORMAT,
                                             locale=LOCALE)

    def __repr__(self) -> str:
        return "{}('{}')".format(self.__class__.__name__, str(self))


class BaseCurrencyType(click.ParamType):

    def convert(self, value: str, param: Any, ctx: Any
                ) -> Union[Currency, Tuple[Currency]]:

        if hasattr(value, '__iter__') and len(value) == 1:
            value = value[0]

        if isinstance(value, str):
            return Currency(str(value))
        else:
            return tuple(map(Currency, iter(value)))


class BasePercentageType(click.ParamType):

    def convert(self, value: str, param: Any, ctx: Any) -> Percentage:
        if hasattr(value, '__iter__') and len(value) == 1:
            value = value[0]

        if isinstance(value, str):
            try:
                return Percentage(str(value))
            except (PercentageOutOfRange, decimal.InvalidOperation) as exc:
                self.fail(exc)
        else:
            try:
                return tuple(map(Percentage, iter(value)))
            except (PercentageOutOfRange, decimal.InvalidOperation) as exc:
                self.fail(exc)


class DeductionsType(BaseCurrencyType):
    name = 'deduction'

    @parse_input_value
    @check_env_dict('deductions')
    def convert(self, value: Union[str, Tuple[str]], param: Any, ctx: Any
                ) -> Union[Currency, Tuple[Currency]]:

        return super().convert(value, param, ctx)


class MarginsType(BasePercentageType):

    name = 'margin'

    @parse_input_value
    @check_env_dict('margins')
    def convert(self, value: Union[str, Tuple[str]], param: Any, ctx: Any
                ) -> Union[Percentage, Tuple[Percentage]]:
        return super().convert(value, param, ctx)


class DiscountsType(BasePercentageType):

    name = 'discount'

    @parse_input_value
    @check_env_dict('discounts')
    def convert(self, value: Union[str, Tuple[str]], param: Any, ctx: Any
                ) -> Union[Percentage, Tuple[Percentage]]:
        return super().convert(value, param, ctx)


class CostsType(BaseCurrencyType):

    name = 'cost'

    @parse_input_value
    def convert(self, value: Union[str, Tuple[str]], param: Any, ctx: Any
                ) -> Union[Currency, Tuple[Currency]]:
        return super().convert(value, param, ctx)


DEDUCTION = DeductionsType()
MARGIN = MarginsType()
DISCOUNT = DiscountsType()
COSTS = CostsType()
