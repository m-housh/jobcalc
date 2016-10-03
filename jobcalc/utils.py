# -*- coding: utf-8 -*-

from typing import Dict, Any, Callable, Union, Tuple
import os
import logging

import click
import colorclass

from .exceptions import NotCallableError

logger = logging.getLogger(__name__)


def _return_input(value: Any) -> Any:
    """Helper to return the input.  This can be used as a valid callback.
    """
    return value


def _converter(cls):
    """Helper to wrap a ``click.ParamType`` as a callback to convert values
    to the appropriate type.
    """
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
    :param error:  If ``True``, raise a ``NotCallableError`` if the callback
                   is not callable. If ``False`` we will return a valid
                   callback, rather than error.  Default is ``True``.

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


def dict_from_env_string(string: Union[str, dict], seperator: str=None,
                         divider: str=None, type: Callable[[Any], Any]=None
                         ) -> Dict[str, Any]:
    """Creates a dict from a string, using a ``seperator`` to seperate the
    items and a ``divider`` to distinguish key, value pairs.

    :param string:  The string to create the dict from.
    :param seperator:  The seperator to use to seperate items in the string.
                       Defaults to ``';'``.  This can also be set by the
                       environment variable ``JOBCALC_SEPERATOR``.
    :param divider:  Divides key, value pairs.  Defaults to ``':'``.  This can
                     also be set by the environment variable
                     ``JOBCALC_DIVIDER``.
    :param type:  Callback to use to convert all the values to a certain type.


    Example::

        >>> dict_from_env_string('standard:5;deluxe:10;premium:15')
        {'standard': '5', 'deluxe': '10', 'premium': '15'}
        >>> dict_from_env_string('standard:5;deluxe:10;premium:15',
        ...                      type=Percentage)
        {'standard': Percentage('0.5'), 'deluxe': Percentage('0.1'),
         'premium': Percentage('0.15')}

    """

    if string is None or string == '':
        return {}
    elif isinstance(string, dict):
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

    split = list(x.split(divider) for x in str(string).split(seperator))
    logger.debug('split: {}'.format(split))

    i = 0
    for item in split:
        if not len(item) == 2:
            logger.debug('invalid item in env_string: {}'.format(item))
            split.pop(i)
        i += 1

    logger.debug('split: {}'.format(split))

    return {
        key: type(value) for (key, value) in split
    }
    '''
    except ValueError:
        # string was invalid, declared a key without a value.
        logger.debug('invalid env string: {}'.format(string))
        raise InvalidEnvString(string)
    '''


def parse_input_string(string: str, seperator: str=';',
                       convert: Callable[[Any], Any]=None) -> Tuple[Any]:
    """Parses an input string that could have multiple values passed in
    from the command line.

    .. note::

        This method always returns a tuple, which can be of length 1 or more.

    :param string:  The input string to parse.
    :param seperator:  The seperator used to seperate items.
                       Defaults to ``';'``.
    :param convert:  A callback that can be used to convert all the parsed
                     values to a type. This can be a ``callable`` that recieves
                     a single value and returns a single value, or we can
                     also handle ``click.ParamType``'s.  Default is ``None``.


    Example::

        >>> parse_input_string('123;456')
        ('123', '456')
        >>> parse_input_string('123;456', convert=Currency)
        (Currency('123'), Currency('456'))
        >>> parse_input_string('123')
        ('123', )

    """

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


def flatten(*args, ignoretypes: Any=str):
    """A generator to flatten iterables, containing single items and possible
    other iterables into a single iterable.

    :param args:  Any value to check for sub-lists (iterable) and flatten.
    :param ignoretypes:  A type or tuple of types to ignore (not flatten).
                         Default is ``str``.

    Example::

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

    .. seealso:: ``colorclass``

    :param string:  The string to colorize.
    :param color:  The color for the string.


    Example::

        >>> colorize('some string', 'red')
        Color('\x1b[31msome string\x1b[39m')

    """
    return colorclass.Color('{' + str(color) + '}' + str(string) +
                            '{/' + str(color) + '}')


def bool_from_env_string(string: str) -> bool:
    """Convert a string recieved from an environment variable into a
    bool.

    'true', 'TRUE', 'TrUe', 1, '1' =  True

    Everything else is False.

    :param string:  The string to convert to a bool.

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
