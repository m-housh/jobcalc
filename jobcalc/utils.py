# -*- coding: utf-8 -*-

from typing import Dict, Any, Callable, Union, Tuple  # , Iterable
import os
import logging
# from collections import namedtuple

import click
import colorclass
# import wrapt

from .exceptions import InvalidEnvString, NotCallableError  # , EnvDictNotFound
# from .config import ENV_PREFIX

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

'''
ENV_PREFIX = 'JOBCALC'
"""The prefix to use for all environment variables associated with the app."""

_Env = namedtuple('_Env', ['MARGINS', 'DISCOUNTS', 'DEDUCTIONS'])

env = _Env(
    MARGINS=ENV_PREFIX + '_MARGINS',
    DISCOUNTS=ENV_PREFIX + '_DISCOUNTS',
    DEDUCTIONS=ENV_PREFIX + '_DEDUCTIONS'
)
"""A named tuple with common environment variable keys."""
'''


def _return_input(value: Any) -> Any:
    """Helper to return the input.  This can be used as a valid callback.
    """
    return value


def _converter(cls):
    if not hasattr(cls, 'convert'):
        raise TypeError('invalid object does not have a convert method')

    def wrapper(value: Any) -> Any:
        return cls.convert(value, None, None)
    return wrapper


def ensure_callback(callback: Callable[[Any], Any], error: bool=True
                    ) -> Callable[[Any], Any]:
    """Ensures that a callback is ``callable``.  Either raising errors or
    returning a valid callback.

    If ``error`` is ``False`` and the callback is not callable, then
    we return a callable that takes a single value as input and returns
    that same value.

    :param callback:  The callback to check.
    :param error:  Boolean to raise a ``NotCallableError`` if the callback
                   is not callable.  Raises errors if ``True``.  Default is
                   ``False``

    :raises  NotCallableError:  If the callback is not callable and ``error``
                                is ``True``.

    """

    if callable(callback):
        # return the value, since it's valid
        return callback
    elif error is True:
        # raise an error, if that's what they want.
        raise NotCallableError(callback)
    # return a valid callable/callback
    return _return_input

'''
def get_env_var(name: str, default: Any=None, use_prefix: bool=True,
                ensure_upper: bool=True, callback: Callable[[Any], Any]=None
                ) -> Any:

    if callback and not callable(callback):
        raise TypeError('callback is not callable: {}'.format(callback))

    name = str(name)

    if use_prefix is True and ENV_PREFIX not in name:
        name = ENV_PREFIX + '_' + name if not name.startswith('_') else \
            ENV_PREFIX + name

    value = os.environ.get(name.upper() if ensure_upper else name, None)
    if value is None:
        return default
    return value if callback is None else callback(value)
'''


def dict_from_env_string(string: Union[str, dict], seperator: str=None,
                         divider: str=None, type: Callable[[Any], Any]=None
                         ) -> Dict[str, Any]:

    if string is None or string == '':
        return {}
    elif isinstance(string, dict):
        # if we passed in an already parsed dict.
        # this is, so that this can be used more easily as callback
        # in ``get_env_var``.
        #
        # :example:
        # get_env_var('SOME_ENV_VAR_THAT_COULD_BE_A_DICT', default={},
        #             callback=parse_env_string)
        return string

    if type and not callable(type):
        raise NotCallableError(type)

    # we need to have type be a callable, to make the dict
    # comprehension work/ easier. So set it to _return_type (which just returns
    # the value) if type is none
    type = type or _return_input

    if seperator is None:
        seperator = os.environ.get('JOBCALC_SEPERATOR', ';')
    else:
        seperator = str(seperator)

    if divider is None:
        divider = os.environ.get('JOBCALC_DIVIDER', ':')
    else:
        divider = str(divider)

    split = (x.split(divider) for x in str(string).split(seperator))

    try:
        return {
            key: type(value) for (key, value) in split
        }
    except ValueError:
        # string was invalid, declared a key without a value.
        logger.debug('invalid env string: {}'.format(string))
        raise InvalidEnvString(string)


def parse_input_string(string: str, seperator: str=';',
                       convert: Callable[[Any], Any]=None) -> Tuple[Any]:

    # handle convert appropriately if it is a ``click.ParamType``,
    # then we use it's convert method.  This is useful if
    # the value is possibly a value in an ``env_dict``
    if convert is not None and isinstance(convert, click.ParamType):
        # use a simple wrapper to wrap to call it's convert method
        # appropriately.
        convert = _converter(convert)
    elif convert is None:
        # falback to the _return_input callback.
        convert = _return_input

    # trim and split the string, based on the ``seperator``
    split = (str(s).strip() for s in str(string).strip().split(seperator)
             if s != '')

    # ``convert`` the items and return as a tuple of items``.
    return tuple(map(convert, split))

'''
# TODO:  This may be able to go away, don't think it's used anywhere.
def check_in_env_dict(key: str, dict_name: str, type: Callable[[Any], Any]=None
                      ) -> Any:
    if type and not callable(type):
        raise NotCallableError(type)

    rv = get_env_var(dict_name, default={},
                     callback=parse_env_string).get(key, key)

    return type(rv) if type is not None else rv
'''


def flatten(*args, ignoretypes: Any=str):
    """A generator to flatten iterables, containing single items and possible
    other iterables into a single iterable.

    :param args:  Any value to check for sub-lists (iterable) and flatten.
    :param ignoretypes:  A type or tuple of types to ignore (not flatten).
                         Default is ``str``.

    :Example:

        >>> list(flatten([1, 2, [3, 4], [5, [6, 7], [8, 9]]]))
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> mylist = ['1', '2', [3, ['4'], ['5 is alive', 6], 7], [8, '9.0']]
        >>> list(flatten(mylist))
        ['1', '2', 3, '4', '5 is alive', 6, 7, 8, '9.0']
        >>> list(flatten([1, 2, (3, 4, 5)], ignoretypes=tuple))
        [1, 2, (3, 4, 5)]

    """
    for value in args:
        if isinstance(value, ignoretypes):
            # don't iterate over strings
            yield value
        elif hasattr(value, '__iter__'):
            for i in flatten(*value, ignoretypes=ignoretypes):
                yield i
        else:
            yield value


def colorize(string: str, color: str) -> colorclass.Color:
    """Returns a colorized string.

    :param string:  The string to colorize.
    :param color:  The color for the string.

    """
    return colorclass.Color('{' + str(color) + '}' + str(string) +
                            '{/' + str(color) + '}')


def bool_from_env_string(string: str) -> bool:
    """Convert a string recieved from an environment variable into a
    bool.

    'true', 'TRUE', 'TrUe', 1, '1' =  True

    Everything else is False.

    """
    if str(string).lower() == 'false' or str(string) == '':
        return False
    if str(string).lower() == 'true':
        return True
    try:
        int_value = int(string)
        if int_value == 1:
            return True
        else:
            return False
    except:
        return False
