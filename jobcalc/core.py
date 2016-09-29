# -*- coding: utf-8 -*-

from typing import Union, Iterable, Any
import logging
# import inspect
import decimal
import collections
import contextlib
import functools

import click

from .utils import flatten, parse_input_string, colorize  # , _return_input
from .types import Currency, Percentage, COSTS, MARGIN, DISCOUNT, DEDUCTION
from .exceptions import InvalidFormatter, HourlyRateError
from .formatters import BaseFormatter, BasicFormatter
from .config import Config, TerminalConfig

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Commonly used Type Hints
CurrencyList = Iterable[Union[Currency, Iterable[Union[Currency, str]], str]]
PercentageList = Iterable[Union[Percentage, str,
                                Iterable[Union[Percentage, str]]]]
FormatterList = Iterable[Union[BaseFormatter, Iterable[BaseFormatter]]]
HoursList = Iterable[Union[str, int, Iterable[Union[str, int]]]]


Context = collections.namedtuple('Context', ('subtotal', 'margin',
                                             'discount', 'deduction'))
"""A namedtuple that represents the args for the ``calculate`` function.
Consists of a ``subtotal``, ``margin``, ``discount``, and ``deduction``.

If these values are set properly then you can call ``calculate(*context)``.
and the values will be unpacked in the correct order.

"""

PromptResponse = collections.namedtuple(
    'PromptRespone', ('value', 'multiple_heading_displayed',
                      'single_heading_displayed')
)


ColorKey = collections.namedtuple('ColorKey', ('margins', 'discounts', 'hours',
                                               'rate', 'deductions', 'costs'))

DEFAULT_COLOR_KEY = ColorKey(
    margins='blue',
    discounts='yellow',
    hours='magenta',
    rate='cyan',
    deductions='red',
    costs='green'
)


def calculate(subtotal: Union[Currency, str]='0',
              margin: Union[Percentage, str]='0',
              multiplier: Union[Percentage, str]='0',
              deduction: Union[Currency, str]='0'
              ) -> Currency:
    """Calculates a total based on the parameters.  Returned as a ``Currency``.

    :param subtotal:  An item that can be converted to a ``Currency`` to be used
                      for the calculation. This would be the sum of all the job
                      costs, materials, hours, etc.
    :param margin:  An item that can be converted to a ``Perentage`` to be used
                    as the profit margin for the calculation.  Default is 0.
    :param multiplier:  An item that can be converted to a ``Percentage`` to
                        be used as a percentage discount in the calculation.
                        This discount comes off after the profit margin has
                        been calculated.  Default is 0.
    :param deduction:  An item that can be converted to a ``Currency`` to be
                       used as a monetary discount in the calculation.  This
                       comes off after the profit margin has be calculated and
                       any other percentage discounts have been taken off.

    """

    return Currency(
        (Currency(subtotal) / (1 - Percentage(margin))) *
        (1 - Percentage(multiplier)) -
        Currency(deduction)
    )


# TODO: Fix this doc string to reflect everything getting stored as lists.
#       And added ``ignore_margins`` for ``subtotal`` to work if costs, include
#       other calculator instances.  Maybe rename ``ignore_margins`` to
#       something more appropriate.  (total_children, or subtotal_children)
class BaseCalculator(object):
    """The ``BaseCalculator`` class know's how to take ``costs``, a ``margin``,
    a ``discount`` (percentage discount), and ``deductions`` and calculate
    a total with those items.

    :param costs:  Either a single item or list of items that can be converted
                   to a ``Currency``.  Whether a single item or a list, these
                   are stored as a list, and the sum of that list is used
                   as the subtotal for the calculation.
    :param margins:  An item that can be converted to a ``Percentage``, used
                    as the profit margin for the calculation.
    :param discounts:  An item that can be converted to a ``Percentage``, used
                      as a percentage discount for the calculation.
    :param deductions:  Either a single item or list of items that can be
                        converted to a ``Currency``.  Whether a single item or
                        a list, these are stored as list, and the sum of that
                        list is used as monetary deduction for the calculation.

    """

    def __init__(self, costs: CurrencyList=[],
                 margins: PercentageList=[],
                 discounts: PercentageList=[],
                 deductions: CurrencyList=[],
                 ignore_margins: bool=None
                 ) -> None:

        self.ignore_margins = ignore_margins

        self.costs = []  # type: CurrencyList
        if costs:
            self.costs.append(costs)

        self.deductions = []  # type: CurrencyList
        if deductions:
            self.deductions.append(deductions)

        self.margins = []  # type: PercentageList
        if margins:
            self.margins.append(margins)

        self.discounts = []  # type: PercentageList
        if discounts:
            self.discounts.append(discounts)

    @contextlib.contextmanager
    def ctx(self, ignore_margins: bool=False) -> Context:
        yield Context(
            subtotal=self.subtotal(ignore_margins=ignore_margins),
            margin=Percentage(sum(map(Percentage, flatten(self.margins)))),
            discount=Percentage(sum(map(Percentage, flatten(self.discounts)))),
            deduction=Currency(sum(map(Currency, flatten(self.deductions))))
        )

    def subtotal(self, ignore_margins: bool=False) -> Currency:
        """Calculate the subtotal of the ``costs``.  This is used because
        ``costs`` can also consist of other calculators, so we call either
        ``total`` or ``subtotal`` accordingly on those items.

        :param ignore_margins:  A boolean, if ``True``, then we call subtotal
                                on child calculators, if it's ``False`` then
                                we call total.  This can also be overriden,
                                by the instance's ``ignore_margins`` attribute.

        """
        totals = []
        for cost in flatten(self.costs):
            # call either ``subtotal`` or ``total`` appropriately, depending
            # on ``ignore_margins`` or ``self.ignore_margins`` setting.
            if isinstance(cost, BaseCalculator):
                if ignore_margins is True or self.ignore_margins is True:
                    # add the subtotal
                    totals.append(cost.subtotal(True))
                else:
                    # add the total, using the margin of the child calculator.
                    totals.append(cost.total())
            else:
                # just append the value
                totals.append(cost)
        # return value of all the totals
        return Currency(sum(map(Currency, totals)))

    def total(self) -> Currency:
        """Calculates the total for the current settings of the instance.

        This method will convert all the items in the ``costs`` and
        ``deductions`` to ``Currency`` instances, which can cause errors
        if the items can not be converted.  The most common error will be
        ``decimal.InvalidOperation``.
        """
        # convert all costs and deductions to Currency items, and let
        # errors propagate up.
        with self.ctx() as ctx:
            return self.calculate(*ctx)

    @staticmethod
    def calculate(*args, **kwargs) -> Currency:
        """Just attaches the ``calculate`` function as a staticmethod.
        This is the method called in ``total``, so if a sub-class would
        like to implement a custom calculation, they can override this
        method.
        """
        return calculate(*args, **kwargs)


class Calculator(BaseCalculator):
    """Extends ``BaseCalculator``.  Adds the ability to attach formatters,
    to ``render`` a formatted output.  Adds ``hours`` and a ``rate`` option.
    The ``hours`` will be summed and multiplied by the ``rate`` and added to
    the ``costs`` of the job.

    :param formatters:  A single or iterable of ``BaseFormatters`` to format
                        the output.
    :param hours:  A single or iterable of items that can be converted to a
                   ``decimal.Decimal``.
    :param rate:  An single item that can be converted to a ``decimal.Decimal``
                  that represents an hourly rate.
    :param config:  A ``Config`` instance to use for values, either set
                    or loaded from the environment.

    """

    def __init__(self, *,
                 formatters: FormatterList=[],
                 hours: HoursList=[],
                 rate: Union[str, int]=None,
                 config: Config=None,
                 **kwargs) -> None:

        super().__init__(**kwargs)

        self.config = config if config is not None else Config()

        self.formatters = []  # type: FormatterList
        if formatters:
            self.formatters.append(formatters)

        self.hours = []  # type: HoursList
        if hours:
            self.hours.append(hours)
        # check in the config for default hours to add.
        if self.config.default_hours != '0':
            self.hours.append(self.config.default_hours)

        self._rate = '0'
        self.rate = rate if rate is not None else self.config.rate

    def subtotal(self, *args, **kwargs) -> Currency:
        """Add's ``costs`` + (``rate`` * ``hours``) for the subtotal."""
        return Currency(
            super().subtotal(*args, **kwargs) + (self.rate * self._hours())
        )

    @property
    def rate(self) -> decimal.Decimal:
        return decimal.Decimal(self._rate)

    @rate.setter
    def rate(self, value: Union[str, int, decimal.Decimal, None]) -> None:
        try:
            rate = decimal.Decimal(value)
            if rate >= 0:
                self._rate = rate
            else:
                logger.debug(
                    'rate is not greater than 0, not changing: {}'.format(rate)
                )
        except (decimal.InvalidOperation, TypeError) as exc:
            logger.debug('Invalid rate, not changing: {}'.format(exc))

    def render(self, seperator: str='\n\n') -> str:
        """Return a string output of all the formatters for an instance.
        Joined by the seperator.

        If no formatters have been set, then we fall back to ``BasicFormatter``,
        which will just output the ``total`` as a formatted currency string.

        :param seperator:  A string to use as the seperator. Defaults to
                           '\n\n'.

        """
        formatters = list(flatten(self.formatters))
        # encase no formatters have been set, just return the
        # total
        if len(formatters) == 0:
            formatters.append(BasicFormatter)

        try:
            # join all the formatters, seperated by ``seperator``
            return str(seperator).join(
                map(lambda formatter: formatter.render(self), formatters)
            )
        except AttributeError as exc:
            # if render failed on an item in formatters, then we had
            # an invalid formatter.
            logger.debug('invalid formatter: {}, exc: {}'.format(
                self.formatters, exc)
            )
            raise InvalidFormatter(self.formatters)

    def _hours(self) -> decimal.Decimal:
        """Helper to return the sum of the hours."""
        return decimal.Decimal(sum(map(decimal.Decimal, flatten(self.hours))))

    def _costs(self) -> decimal.Decimal:
        """Helper to return the sum of the costs."""
        return decimal.Decimal(sum(map(decimal.Decimal, flatten(self.costs))))

    @contextlib.contextmanager
    def ctx(self, strict: bool=False) -> Context:
        """Return a properly configured ``Context`` to be used.

        .. note::

            This can also raise errors if ``hours`` or ``rate`` can not
            be converted to a ``decimal.Decimal``.  Most common error will
            be a ``decimal.InvalidOperation`` error.


        :param strict:  Will cause an error to be raised if ``hours`` are
                        set on an instance, but an ``rate`` has not been set.

        :raises HourlyRateError:  If ``strict`` is ``True`` and no hourly rate
                                  has been set.

        """
        # these can raise errors, if the values can not be
        # converted to ``Decimal``'s
        logger.debug('rate: {}'.format(self.rate))
        rate = decimal.Decimal(self.rate)
        hours = self._hours()

        if hours > 0 and not rate > 0:
            # log a warning that hours have been set, but no hourly rate
            # has been set.
            logger.warning(
                'hours: {}, are set but rate: {} has not been set'.format(
                    hours, rate)
            )
            if strict is True:
                # raise an error, if they want one.
                raise HourlyRateError()

        with super().ctx() as ctx:
            yield ctx

        '''
        with super().ctx() as ctx:
            # calculate the new subtotal with our hours and rate,
            # which can be 0 * 0
            subtotal = Currency(ctx.subtotal + (hours * rate))
            yield Context(
                subtotal=subtotal,
                margin=ctx.margin,
                discount=ctx.discount,
                deduction=ctx.deduction
            )
        '''

    def update(self, *, append: bool=True, **kwargs) -> None:

        for key in kwargs:
            logger.debug(
                'updating key: {}, value: {}'.format(key, kwargs[key])
            )
            inconfig = False
            attr = getattr(self, key, None)
            # check if it's in the config.
            if attr is None:
                attr = getattr(self.config, key, None)
                inconfig = True

            if isinstance(attr, list) and append is True:
                attr.append(kwargs[key])
            elif isinstance(attr, list) and append is False:
                setattr(self, key, [kwargs[key]])
            else:
                if key == 'rate':
                    self.rate = kwargs[key]
                elif inconfig is False:
                    logger.debug('inconfig is false')
                    setattr(self, key, kwargs[key])
                else:
                    logger.debug('inconfig')
                    setattr(self.config, key, kwargs[key])


# TODO:  Add a prompt seperator environment/config setting. To be used
#        when prompting for values that can have multiples.
class TerminalCalculator(Calculator):

    _prompts = ('margin', 'discount', 'hours', 'rate', 'deduction', 'cost')

    def __init__(self, *, colors: ColorKey=None, **kwargs) -> None:
        kwargs.setdefault('config', TerminalConfig())
        super().__init__(**kwargs)
        self.colors = colors if colors is not None else DEFAULT_COLOR_KEY

    '''
    @staticmethod
    def _confirm_prompt(category: str) -> bool:
        msg = "Would you like to add this to {}?".format(category)
        return click.confirm(msg)
    '''

    def _multiple_display_header(self) -> str:
        return "\nMultiples accepted, they can be seperated by '{}'\n".format(
            self.config.prompt_seperator
        )

    def _single_display_header(self) -> str:
        return '\nSingle value only.\n'

    def _prompt_for(self, attr: str, default: Any=None, type: Any=None,
                    confirm: bool=True, is_single: bool=False,
                    current: Any=None, display_multiple_header: bool=True,
                    display_single_header: bool=True
                    ) -> PromptResponse:
        """A helper to prompt a user for extra information for an attribute.
        """
        # search for color in ``self.colors``
        attr_string_color = getattr(self.colors, str(attr), 'red')

        # colorize the string of the attribute we're prompting for.
        attr_string = colorize(str(attr), attr_string_color)

        # get the seperator used to split multiple values in user input.
        seperator = self.config.prompt_seperator

        # whether we are/have displayed the multiple header
        multiple_heading_displayed = not display_multiple_header
        # whether we are/have displayed the single header
        single_heading_displayed = not display_single_header

        # validate that we are prompting for a valid attribute.
        if getattr(self, str(attr), None) is None:
            raise AttributeError(attr)

        # start building our display message.
        msg = ''

        if multiple_heading_displayed is False and is_single is False:
            # add the multiple display header to inform a user that
            # multiple values are accepted and what should be used as
            # the seperator.
            multiple_heading_displayed = True
            msg += self._multiple_display_header()

        if single_heading_displayed is False and is_single is True:
            # add the single display heading to inform the user that
            # only single values are accepted.
            single_heading_displayed = True
            msg += self._single_display_header()

        msg += 'Please enter {} for the job'.format(
            'a ' + attr_string if is_single is True else attr_string
        )

        # show the current value, if applicable.
        if current is not None:
            msg += " Current value is: '{}'".format(current)

        # prompt for the value(s) from user.
        _value = click.prompt(msg, default=default, type=str)
        logger.debug('pre-parsed value: {}'.format(_value))

        # parse the input value, converting to the expected type,
        # if applicable.
        #
        # parse_input_string is always a tuple return value.
        rv = parse_input_string(_value, seperator=seperator, convert=type)

        if is_single is False:
            # then a tuple is ok to return, so return rv
            return PromptResponse(
                value=rv,
                multiple_heading_displayed=multiple_heading_displayed,
                single_heading_displayed=single_heading_displayed
            )
        else:
            # just return the first value of the tuple
            return PromptResponse(
                value=rv[0],
                multiple_heading_displayed=multiple_heading_displayed,
                single_heading_displayed=single_heading_displayed
            )

    prompt_for_cost = functools.partialmethod(_prompt_for,
                                              'costs', type=COSTS)

    prompt_for_margin = functools.partialmethod(_prompt_for,
                                                'margins', type=MARGIN)

    prompt_for_discount = functools.partialmethod(_prompt_for,
                                                  'discounts', type=DISCOUNT)

    prompt_for_deduction = functools.partialmethod(_prompt_for,
                                                   'deductions',
                                                   type=DEDUCTION)

    prompt_for_hours = functools.partialmethod(_prompt_for,
                                               'hours', type=decimal.Decimal)

    prompt_for_rate = functools.partialmethod(_prompt_for,
                                              'rate', type=decimal.Decimal,
                                              confirm=False, is_single=True)

    def key_for_prompt(self, prompt: str) -> str:
        """A helper to return the correct key (attribute name) to use for
        a prompt.

        This is helpful when making multiple prompts that save their values
        in a dict, that later is used to update the attributes on an instance.

        """
        prompt = str(prompt)
        if prompt not in self._prompts and prompt.endswith('s'):
            # check if someone is asking for a key that could be valid, just
            # used the plural form.
            # chop of the 's' and check again.
            prompt = prompt[:-1]

        if prompt not in self._prompts:
            raise AttributeError(prompt)

        if prompt == 'rate' or prompt == 'hours':
            return prompt
        else:
            # all other attribute names end in 's', so we add it to the
            # value we return.
            return prompt + 's'

    @contextlib.contextmanager
    def prompt_for(self, prompt: str, **kwargs) -> PromptResponse:
        """A context manager that prompt's a user for input, and yields a
        ``PromptResponse``.

        """
        prompt = str(prompt)
        if prompt not in self._prompts and prompt.endswith('s'):
            # perhaps a user added an 's'
            # ex. prompt_for('margins') instead of prompt_for('margin'),
            # so let's check.
            # chop off the 's' and see what happens.
            prompt = prompt[:-1]

        func = getattr(self,  'prompt_for_' + prompt, None)

        if prompt not in self._prompts or func is None:
            raise AttributeError(prompt)

        yield func(**kwargs)

    # TODO: clean this up/ refractor.
    def prompt_for_empty(self, strict: bool=False) -> None:

        # holds values that we've prompted for.
        updates = {}

        # we only want to display the headings once, so these
        # determine if we have displayed the headings or not already.
        multiple_heading_displayed = False
        single_heading_displayed = False

        # if ``strict`` is True, then errors get raised if ``hours`` have
        # been set with no ``rate`` set.
        with self.ctx(strict=strict) as ctx:
            # show the values before any prompts, if applicable.
            logger.debug('ctx before prompts: {}, hours: {}, rate: {}'.format(
                ctx, self._hours(), self.rate))

            # ``self._prompts`` contain the valid prompt key's to use,
            # and the order in which we prompt for empty's.
            for prompt in self._prompts:

                # ``current`` only get's set for hours in this context, if
                # there are ``default_hours`` added from an environment
                # variable.
                current = None

                # determine the value to check if it's 0, if so,
                # then we prompt
                if prompt == 'hours':
                    # hours can consist of default hours set by
                    # environment variable ``JOBCALC_DEFAULT_HOURS``.
                    # so we need to check if there is a value there and
                    # subtract it from the hours set on an instance, to
                    # decide if hours is empty or not.
                    default_hours = int(self.config.default_hours)
                    value = self._hours()
                    if default_hours > 0:
                        value = value - int(self.config.default_hours)
                        current = default_hours
                elif prompt == 'rate':
                    # value for a rate prompt is ``self.rate``
                    value = self.rate
                elif prompt == 'cost':
                    # value for cost prompt is ``self._costs``, which is the
                    # sum of our ``costs`` for an instance.
                    value = self._costs()
                else:
                    # else get the value from the ctx
                    value = getattr(ctx, prompt, None)

                if value == 0:
                    # setup kwargs to pass to the ``prompt_for`` method.
                    prompt_kwargs = dict(
                        default='0',
                        confirm=False,
                        current=current,
                        display_multiple_header=not multiple_heading_displayed,
                        display_single_header=not single_heading_displayed
                    )

                    with self.prompt_for(prompt, **prompt_kwargs) as result:

                        value = result.value
                        multiple_heading_displayed = \
                            result.multiple_heading_displayed
                        single_heading_displayed = \
                            result.single_heading_displayed

                        # get the valid key to use for the prompt.
                        key = self.key_for_prompt(prompt)
                        # set the value for key in updates.
                        updates[key] = value
            # update ``self`` with the value(s) we've prompted for.
            self.update(**updates)
        # show the changes that have been applied if ``debug`` is True.
        if self.config.debug is True:
            with self.ctx(strict=False) as ctx:
                logger.debug('ctx after prompts: {}'.format(ctx))
