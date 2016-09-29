# -*- coding: utf-8 -*-

from typing import Any  # , Any
import logging
from collections import namedtuple
import contextlib
import decimal

import terminaltables
import colorclass

from .utils import colorize
from .types import Currency, Percentage

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


ColorContext = namedtuple('ColorContext', ('subtotal', 'margin', 'discount',
                                           'deduction', 'total'))
TotaledContext = namedtuple('TotaledContext', ColorContext._fields)


DEFAULT_COLORS = ColorContext(
    subtotal='magenta',
    margin='blue',
    discount='yellow',
    deduction='red',
    total='green'
)

DEFAULT_FORMULA_STRING = """
color key: {header}


{subtotal_string}

(
    (({subtotal} / (1 - {margin}) * (1 - {discount})) - {deduction}) = {total}
)
"""


class BaseFormatter(object):

    @staticmethod
    def colorize(*items) -> colorclass.Color:
        """If an item is a ``Currency`` or ``Percentage``, then
        call it's ``formatted_string`` method, before colorizing the
        value.

        :param items:  A 2 tuple (item, color).  Where item 1 can be a string,
                       Currency, or Percentage, and item 2 (color) should be a
                       string that can be converted to a ``colorclass.Color``.

        :raises ValueError:  If items does not have enough items in it.

        """

        # let this raise a ``ValueError`` if it does not work.
        item, color = items[0], items[1]

        if isinstance(item, (Currency, Percentage)):
            item = item.formatted_string()
        return colorize(item, color)

    @staticmethod
    def render(calculator) -> str:
        raise NotImplementedError()

    @staticmethod
    @contextlib.contextmanager
    def totaled_ctx(calculator: Any) -> TotaledContext:
        with calculator.ctx() as ctx:
            yield TotaledContext(*list(ctx) + [calculator.total()])


class BasicFormatter(BaseFormatter):
    @staticmethod
    def render(calculator: Any) -> str:
        try:
            return calculator.total().formatted_string()
        except AttributeError as exc:
            logger.debug('failed render for calculator: {}, exc: {}'.format(
                calculator, exc)
            )
            raise TypeError("'{}' should inherit from BaseCalculator".format(
                calculator)
            )


class TerminalFormatter(terminaltables.AsciiTable, BaseFormatter):
    """A ``terminaltables.AsciiTable``, that supports colors and
    a title.

    :param colors:  A 5 tuple or ``ColorContext`` of strings that can
                    be used by to convert an item to a ``colorclass.Color``.
                    Defaults to (subtotal='magenta', margin='blue',
                    discount='yellow', deduction='red', total='green').
    :param title:  A title for the table.  Defaults to ``'DETAILED'``.  If you
                   do not want a title, then this can be set to ``None``
    :param no_colors:  If ``True``, turns off colored output for the table.
                       Default is ``False``.
    :param color_header:  If ``True`` then colorize the header as well.
                          Default is ``False``.

    """

    def __init__(self, *colors, title: str='DETAILED', no_colors: bool=False,
                 color_header: bool=False):

        super().__init__([], title=title)

        if colors and no_colors is False:
            self.colors = ColorContext(*colors)
        elif no_colors is False:
            self.colors = DEFAULT_COLORS

        self.no_colors = no_colors
        self.color_header = color_header

    def render(self, calculator: Any) -> str:
        """Set's up the table, and returns it as a string, to be rendered.

        :param calculator:  The calculator to create a table for.  Should
                            be a ``BaseCalculator`` or sub-class.

        """
        with calculator.ctx() as ctx:
            headers = TotaledContext(*map(lambda x: x.upper(),
                                          TotaledContext._fields))

            if self.color_header is True:
                headers = list(map(lambda x: self.colorize(*x),
                                   zip(headers, self.colors)))

            body = list(ctx)
            body.append(Currency(calculator.total()))

            if self.no_colors is False:
                body = list(map(lambda items: self.colorize(*items),
                                zip(body, self.colors)))

            logger.debug('body: {}'.format(body))

            self.table_data = [headers, body]

        return self.table


# TODO: Create a ``ColorContextError`` to raise instead of ``TypeError``
#       if colors is the wrong size.
class FormulaFormatter(BaseFormatter):
    """Prints the formula used for the calculations.

    :param colors:  A 5 tuple or ``ColorContext`` of strings that can
                    be used by to convert an item to a ``colorclass.Color``.
                    Defaults to (subtotal='magenta', margin='blue',
                    discount='yellow', deduction='red', total='green').
    :param formula_string:  A string to use for the format. This should be a
                            a string that we call ``format``, that accepts
                            kwargs (header, subtotal, margin, discount,
                            deduction, and total).  Defaults to
                            ``DEFAULT_FORMULA_STRING``.
    :param no_color:  Turns colored output off.
    :param title:  Title to display before the output.

    :raises TypeError:  If colors is not a 5 tuple.

    """

    def __init__(self, *colors, formula_string: str=None, no_color: bool=False,
                 title: str='FORMULA') -> None:

        self.title = title

        if colors and no_color is False:
            # convert the colors to a ``ColorContext``
            # this can raise ``TypeError`` if not enough or too many values.
            self.colors = ColorContext(*colors)
        elif no_color is False:
            # set the colors to the default
            self.colors = DEFAULT_COLORS

        self.no_color = no_color

        # set the formula string to use for this instance.
        if formula_string:
            self.formula_string = formula_string
        else:
            self.formula_string = DEFAULT_FORMULA_STRING

    def render(self, calculator: Any) -> str:
        """Render a formula string used for a ``BaseCalculator`` instance or
        sub-class.

        :param calculator:  A ``BaseCalculator`` or sub-class to use as the
                            context for the output.

        """

        with self.totaled_ctx(calculator) as ctx:
            # find the hours and rate to build the subtotal
            # formula
            hours = calculator._hours()
            rate = decimal.Decimal(str(calculator.rate))

            # format a subtotal formula string.
            subtotal_string = \
                'subtotal = ({costs} + ({hours} * {rate}))'.format(
                    costs=ctx.subtotal - (hours * rate),
                    hours=hours,
                    rate=rate)

            # colorize if applicable.
            if self.no_color is False:
                ctx = TotaledContext(*map(lambda x: self.colorize(*x),
                                          zip(ctx, self.colors)))
                header = ' '.join(map(lambda x: self.colorize(*x),
                                      zip(ctx._fields, self.colors)))
            else:
                ctx = TotaledContext(*map(lambda x: x.formatted_string(), ctx))
                header = ' '.join(ctx._fields)

            # get the values from the context, either colored or not,
            # and add our headers.
            values = ctx._asdict()
            values['header'] = header
            values['subtotal_string'] = subtotal_string
            # format the string (``self.formual_string``)
            formatted = self.formula_string.format(**values)

            # build and return the final output string.
            return '\n'.join((self.title, '-' * len(self.title),
                              formatted))
