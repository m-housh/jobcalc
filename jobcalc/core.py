# -*- coding: utf-8 -*-

from typing import Union, Iterable, Any, Dict
import logging
# import inspect
import decimal
import collections
import contextlib
import functools

import click

from .utils import flatten, parse_input_string, colorize  # , _return_input
from .param_types import Currency, Percentage, COSTS, MARGIN, DISCOUNT, \
    DEDUCTION
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
"""A namedtuple that represents the args for the :py:meth:`calculate` function.

If these values are set properly then you can call ``calculate(*context)``.
and the values will be unpacked in the correct order.

:param subtotal:  The subtotal for the calculation.
:param margin:  The margin for the calculation
:param discount:  The percentage discount for the calculation.
:param deduction:  The monetary deduction for the calculation.

Example::

    >>> ctx = Context(subtotal='123', margin='50', discount='10',
    ...               deduction='0')
    >>> calculate(*ctx).formatted_string()
    '$221.40'

"""

PromptResponse = collections.namedtuple(
    'PromptRespone', ('value', 'multiple_heading_displayed',
                      'single_heading_displayed')
)
"""A namedtuple that represents the response to prompting for user input.

:param value: The parsed value from the user input.
:param multiple_heading_displayed: A boolean that indicates if we displayed
                                    the multiple value heading during a prompt.
:param single_heading_displayed: A boolean that indicates if we displayed
                                  the single value heading during a prompt.

"""


ColorKey = collections.namedtuple('ColorKey', ('margins', 'discounts', 'hours',
                                               'rate', 'deductions', 'costs'))
"""A namedtuple that can be used to declare colors to be used when prompting
for user input.

.. note::

    See ``colorclass`` for valid colors.

:param margins: Color when prompting for margin.
:param discounts:  Color when prompting for discounts.
:param hours:  Color when prompting for hours.
:param rate:  Color when prompting for rate.
:param deductions:  Color when prompting for deductions.
:param costs:  Color when prompting for costs.

"""

DEFAULT_COLOR_KEY = ColorKey(
    margins='blue',
    discounts='yellow',
    hours='magenta',
    rate='cyan',
    deductions='red',
    costs='green'
)
"""The default colors to fallback to if none are declared for a calculator."""


def calculate(subtotal: Union[Currency, str]='0',
              margin: Union[Percentage, str]='0',
              multiplier: Union[Percentage, str]='0',
              deduction: Union[Currency, str]='0'
              ) -> Currency:
    """Calculates a total based on the parameters.  Returned as a ``Currency``.

    :param subtotal: An item that can be converted to a ``Currency`` to be used
                      for the calculation. This would be the sum of all the job
                      costs, materials, hours, etc.
    :param margin: An item that can be converted to a ``Perentage`` to be used
                    as the profit margin for the calculation.  Default is 0.
    :param multiplier: An item that can be converted to a ``Percentage`` to
                        be used as a percentage discount in the calculation.
                        This discount comes off after the profit margin has
                        been calculated.  Default is 0.
    :param deduction: An item that can be converted to a ``Currency`` to be
                       used as a monetary discount in the calculation.  This
                       comes off after the profit margin has be calculated and
                       any other percentage discounts have been taken off.

    """

    return Currency(
        (Currency(subtotal) / (1 - Percentage(margin))) *
        (1 - Percentage(multiplier)) -
        Currency(deduction)
    )


class BaseCalculator(object):
    """The ``BaseCalculator`` class know's how to take ``costs``, a ``margin``,
    a ``discount`` (percentage discount), and ``deductions`` and calculate
    a total with those items.

    All items can be either single or iterables of items, but all get stored
    as a list.  And the sum of that list of items makes up the total for a
    given item.

    :param costs:  Either a single item or list of items that can be converted
                   to a :py:class:`Currency`, used as the subtotal for a
                   calculation.
    :param margins:  An item or list of items that can be converted to a
                     :py:class:`Percentage`, used as the profit margin for the
                     calculation.
    :param discounts:  An item or list of items that can be converted to a
                       :py:class:`Percentage`, used as a percentage discount
                       for the calculation.
    :param deductions:  An item or list of items that can be converted to a
                        :py:class:`Currency`, used as monetary deduction for
                        the calculation.
    :param ignore_margins:  A bool determining whether to ignore margins if
                            any of the items in ``costs`` are other
                            ``Calculator`` instances. Defaults to ``False``.

    """

    def __init__(self, costs: CurrencyList=[],
                 margins: PercentageList=[],
                 discounts: PercentageList=[],
                 deductions: CurrencyList=[],
                 ignore_margins: bool=None
                 ) -> None:

        self.ignore_margins = bool(ignore_margins) if ignore_margins is not \
            None else False

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
    def ctx(self, ignore_margins: bool=None) -> Context:
        """A context manager that yields a ``Context`` that is properly set
        up to be used in a calculation.

        :param ignore_margins:  A bool to determine whether to ignore margins
                                in the ``subtotal`` if our ``costs`` include
                                other ``Calculator`` instances.  This will
                                fallback to ``self.ignore_margins`` if not
                                supplied.

        """
        ignore_margins = bool(ignore_margins) if ignore_margins is not None \
            else self.ignore_margins

        yield Context(
            subtotal=self.subtotal(ignore_margins=ignore_margins),
            margin=Percentage(sum(map(Percentage, flatten(self.margins)))),
            discount=Percentage(sum(map(Percentage, flatten(self.discounts)))),
            deduction=Currency(sum(map(Currency, flatten(self.deductions))))
        )

    def subtotal(self, ignore_margins: bool=None) -> Currency:
        """Calculate the subtotal of the ``costs``.  This is used because
        ``costs`` can also consist of other calculators, so we call either
        :py:meth:`total` or :py:meth:`subtotal` accordingly on those items.

        :param ignore_margins:  A boolean, if ``True``, then we call subtotal
                                on child calculators, if it's ``False`` then
                                we call total.  We fallback to
                                ``self.ignore_margins`` if this is not passed
                                in.

        """
        ignore_margins = bool(ignore_margins) if ignore_margins is not None \
            else self.ignore_margins

        totals = []
        for cost in flatten(self.costs):
            # call either ``subtotal`` or ``total`` appropriately, depending
            # on ``ignore_margins`` or ``self.ignore_margins`` setting.
            if isinstance(cost, BaseCalculator):
                if ignore_margins is True:
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

        This method will convert all the items in to their appropriate type,
        which can cause errors if the items can not be converted properly.
        The most common error will be ``decimal.InvalidOperation``.

        """
        # convert all costs and deductions to Currency items, and let
        # errors propagate up.
        with self.ctx() as ctx:
            return self.calculate(*ctx)

    @staticmethod
    def calculate(*args, **kwargs) -> Currency:
        """Just attaches the :py:func:`calculate` function as a staticmethod.
        This is the method called in :py:meth:`total`, so if a sub-class would
        like to implement a custom calculation, they can override this
        method.

        """
        return calculate(*args, **kwargs)


class Calculator(BaseCalculator):
    """Extends :py:class:`BaseCalculator`.  Adds the ability to attach
    formatters, to ``render`` a formatted output.  Adds ``hours`` and a
    ``rate`` option. The ``hours`` will be summed and multiplied by the
    ``rate`` and added to the ``subtotal`` of the job.
    Also adds the ability to pass in a :py:class:`Config` instance for
    common configuration of a ``Calculator``.

    :param formatters:  A single or iterable of :py:class:`BaseFormatter`'s to
                        format the output.
    :param hours:  A single or iterable of items that can be converted to a
                   ``decimal.Decimal``.
    :param rate:  An single item that can be converted to a ``decimal.Decimal``
                  that represents an hourly rate.
    :param config:  A :py:class:`Config` instance to use for values, either set
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

    def subtotal(self, **kwargs) -> Currency:
        """Add's sum of ``costs`` + (``rate`` * ``hours``) for the subtotal.

        :param kwargs:  Get passed to ``super``'s subtotal method.

        """
        return Currency(
            super().subtotal(**kwargs) + (self.rate * self._hours())
        )

    @property
    def rate(self) -> decimal.Decimal:
        """Used as the hourly rate for a calculator.  Defaults to '0'.  This
        will not accept anything that is not greater or equal to 0 or anything
        that can not be converted to a ``decimal.Decimal``.

        """
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

        If no formatters have been set, then we fall back to
        :py:class`BasicFormatter`, which will just output the
        :py:meth:`total` as a formatted currency string.

        :param seperator:  A string to use as the seperator. Defaults to
                           a double new-line.

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
        """Helper to return the sum of the costs, not including hours and rate.
        """
        return decimal.Decimal(sum(map(decimal.Decimal, flatten(self.costs))))

    @contextlib.contextmanager
    def ctx(self, strict: bool=False) -> Context:
        """Return a properly configured :py:class:`Context` to be used.

        .. note::

            This can also raise errors if ``hours`` or ``rate`` can not
            be converted to a ``decimal.Decimal``.  Most common error will
            be a ``decimal.InvalidOperation`` error.


        :param strict:  If ``True`` an error will be raised if ``hours`` are
                        set on an instance, but no :py:attr:`rate` has been
                        set. Default is ``False``

        :raises HourlyRateError:  If ``strict`` is ``True`` and no hourly rate
                                  has been set.

        """
        # these can raise errors, if the values can not be
        # converted to ``Decimal``'s
        rate = decimal.Decimal(self.rate)
        hours = self._hours()

        if hours > 0 and not rate > 0:
            # log a warning that hours have been set, but no hourly rate
            # has been set.
            logger.debug(
                'hours: {}, are set but rate: {} has not been set'.format(
                    hours, rate)
            )
            if strict is True:
                # raise an error, if they want one.
                raise HourlyRateError()

        with super().ctx() as ctx:
            yield ctx

    def update(self, updates: Dict[str, Any]=None, append: bool=True, **kwargs
               ) -> None:
        """A convenience method to update the common items of an instance.

        :param updates:  Optional dict used for the updates where the
                         keys are attribute names and the values are the items
                         to set for the attribute.
        :param append:  A bool, if ``True`` then we add the items to the
                        existing attribute, if ``False`` then we remove any
                        items already set with the new items.  Default is
                        ``True``.
        :param kwargs:  Same as ``updates``.

        Example::

            >>> calc = Calculator()
            >>> calc.update({'margins': '50'})
            >>> assert calc.margins[-1] == '50'
            # True
            >>> calc.update(costs='123')
            >>> assert calc.costs[-1] == '123'
            # True

        """

        if updates is not None and not isinstance(updates, dict):
            raise TypeError("'{}' should be a dict.")
        if updates is not None:
            kwargs.update(updates)

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
                    setattr(self, key, kwargs[key])
                else:
                    setattr(self.config, key, kwargs[key])


# TODO: Add an error if colors does not convert to a ``ColorKey``
class TerminalCalculator(Calculator):
    """Extends :py:class:`Calculator` for use in the command line interface.

    :param colors: A 6 tuple or :py:class:`ColorKey` of colors
    :param kwargs: Extra args to pass to :py:class:``Calculator``

    """

    # the valid prompt key's and the order we want to prompt
    _prompts = (
        # multiple values accepted
        'margin', 'discount', 'hours', 'deduction', 'cost',

        # single values accepted
        'rate'
    )

    def __init__(self, *, colors: Union[Iterable[str], ColorKey, None]=None,
                 **kwargs) -> None:
        kwargs.setdefault('config', TerminalConfig())
        super().__init__(**kwargs)
        self.colors = ColorKey(*colors) if colors is not None else \
            DEFAULT_COLOR_KEY

    '''
    @staticmethod
    def _confirm_prompt(category: str) -> bool:
        msg = "Would you like to add this to {}?".format(category)
        return click.confirm(msg)
    '''

    def _multiple_display_header(self) -> str:
        """Formats and returns the header shown when prompting for multiple
        values from the user.
        """
        rv = \
            "\nMultiples accepted, they can be seperated by '{}'\n\n".format(
                self.config.prompt_seperator)
        return rv

    def _single_display_header(self) -> str:
        return '\nSingle value only.\n\n'

    def _prompt_for(self, attr: str, default: Any=None, type: Any=None,
                    is_single: bool=False, current: Any=None,
                    display_multiple_header: bool=True,
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
    """Prompt the user for cost(s) for the calculation.

    :param default:  Optional value to use as default for no input.
    :param current: Optional value to display as the current value.
    :param is_single: If input is single or accepts multiple values.
    :param type:  A type to convert the value(s) to.
    :param display_multiple_header:  If ``True`` then show the multiple value
                                     header.
    :param display_single_header:  If ``True`` then show the single value
                                   header.

    :rtype:  :py:class:`.PromptResponse`
    """

    prompt_for_margin = functools.partialmethod(_prompt_for,
                                                'margins', type=MARGIN)
    """Prompt the user for margin(s) for the calculation.

    :param default:  Optional value to use as default for no input.
    :param current: Optional value to display as the current value.
    :param is_single: If input is single or accepts multiple values.
    :param type:  A type to convert the value(s) to.
    :param display_multiple_header:  If ``True`` then show the multiple value
                                     header.
    :param display_single_header:  If ``True`` then show the single value
                                   header.

    :rtype:  :py:class:`.PromptResponse`
    """

    prompt_for_discount = functools.partialmethod(_prompt_for,
                                                  'discounts', type=DISCOUNT)
    """Prompt the user for discount(s) for the calculation.

    :param default:  Optional value to use as default for no input.
    :param current: Optional value to display as the current value.
    :param is_single: If input is single or accepts multiple values.
    :param type:  A type to convert the value(s) to.
    :param display_multiple_header:  If ``True`` then show the multiple value
                                     header.
    :param display_single_header:  If ``True`` then show the single value
                                   header.

    :rtype:  :py:class:`.PromptResponse`
    """

    prompt_for_deduction = functools.partialmethod(_prompt_for,
                                                   'deductions',
                                                   type=DEDUCTION)
    """Prompt the user for deduction(s) for the calculation.

    :param default:  Optional value to use as default for no input.
    :param current: Optional value to display as the current value.
    :param is_single: If input is single or accepts multiple values.
    :param type:  A type to convert the value(s) to.
    :param display_multiple_header:  If ``True`` then show the multiple value
                                     header.
    :param display_single_header:  If ``True`` then show the single value
                                   header.

    :rtype:  :py:class:`.PromptResponse`
    """

    prompt_for_hours = functools.partialmethod(_prompt_for,
                                               'hours', type=decimal.Decimal)
    """Prompt the user for hour(s) for the calculation.

    :param default:  Optional value to use as default for no input.
    :param current: Optional value to display as the current value.
    :param is_single: If input is single or accepts multiple values.
    :param type:  A type to convert the value(s) to.
    :param display_multiple_header:  If ``True`` then show the multiple value
                                     header.
    :param display_single_header:  If ``True`` then show the single value
                                   header.

    :rtype:  :py:class:`.PromptResponse`
    """

    prompt_for_rate = functools.partialmethod(_prompt_for,
                                              'rate', type=decimal.Decimal,
                                              is_single=True)
    """Prompt the user for a rate for the calculation.

    :param default:  Optional value to use as default for no input.
    :param current: Optional value to display as the current value.
    :param is_single: If input is single or accepts multiple values.
    :param type:  A type to convert the value(s) to.
    :param display_multiple_header:  If ``True`` then show the multiple value
                                     header.
    :param display_single_header:  If ``True`` then show the single value
                                   header.

    :rtype:  :py:class:`.PromptResponse`

    """

    def key_for_prompt(self, prompt: str) -> str:
        """A helper to return the correct key (attribute name) to use for
        a prompt.

        This is the opposite of the :py:meth:`normalize` method.  In which
        it ensures the return value is pluralized for most cases as that's
        the key that can be used in the :py:meth:`update` method for an
        instance.

        This is helpful when making multiple prompts that save their values
        in a dict, that later is used to update the attributes on an instance.

       :param prompt:  The attribute the prompt is for.

        Example::

            >>> calc = TerminalCalculator()
            >>> calc.key_for_prompt('discount')
            'discounts'
            >>> calc.key_for_prompt('rates') # handle accidental plural's
            'rate'

        """
        prompt = str(prompt)
        if prompt not in self._prompts and prompt.endswith('s'):
            # check if someone is asking for a key that could be valid, just
            # used the plural form.
            # chop of the 's' and check again.
            prompt = prompt[:-1]
        elif prompt not in self._prompts and not prompt.endswith('s'):
            # try adding an 's' to see what happens.
            prompt += 's'

        if prompt not in self._prompts:
            raise AttributeError(prompt)

        if prompt == 'rate' or prompt == 'hours':
            return prompt
        else:
            # all other attribute names end in 's', so we add it to the
            # value we return.
            return prompt + 's'

    def normalize(self, attr: str) -> str:
        """A helper to normalize an attribute name, as most context's expect
        the name to not be pluralized (except ``hours``), so we chop off the
        's' if applicable.

        This is also helpful if using :py:meth:`prompt_for` method, to make
        sure the name for the prompt is correct.

        :param attr:  The attribute name to normalize.

        """
        attr = str(attr)
        if attr != 'hours' and attr.endswith('s'):
            attr = attr[:-1]
        return attr

    def is_empty(self, attr: str) -> bool:
        """Determines if an attribute is considered empty, or equal to
        '0'.

        If there are default hours set by an environment variable, then
        hours are considered empty if the sum of (hours - default_hours) are
        '0'.

        :param attr:  The name of the attribute to check.

        """
        attr = self.normalize(attr)

        if attr == 'rate':
            # check rate against ``self.rate()``
            return self.rate == 0
        if attr == 'hours':
            # check hours, which can also have ``default_hours`` that are
            # loaded from an envrionment variable, so we check that as well.
            # hours is considered empty if hours - default_hours == 0.
            hours = self._hours()
            default_hours = int(self.config.default_hours)
            return (hours - default_hours) == 0
        if attr == 'cost':
            # check cost against ``self._costs()``.
            return self._costs() == 0
        # everything else get's checked in ``self.ctx``
        with self.ctx() as ctx:
            value = getattr(ctx, attr, None)
            if value is None:
                # if we are None, then someone is checking for unsupported
                # attribute.
                raise AttributeError(attr)
            return value == 0

    @contextlib.contextmanager
    def prompt_for(self, prompt: str, **kwargs) -> PromptResponse:
        """A context manager that prompt's a user for input, and yields a
        ``PromptResponse``.

        Valid prompts are 'margin', 'discount', 'deduction', 'cost', 'hours',
        and 'rate'.  We will also do/ call the right method if use the plural
        form of prompt (ex. 'margins').

        :param prompt:  The attribute to prompt for (ex. 'margin')
        :param kwargs:  They get passed to the prompt_for_{prompt} command.

        Example::

            >>> calc = TerminalCalculator()
            >>> with calc.prompt_for('margin', default='0') as result:
            ...    calc.update(margins=result.value)

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

    def prompt_for_empty(self) -> None:
        """Prompt the user for all the values that are determined to
        be empty or '0', and add them to instance appropriately.

        """

        # we only want to display the headings once, so these
        # determine if we have displayed the headings or not already.
        multiple_heading_displayed = False
        single_heading_displayed = False
        strict = False

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

            # check if the value is empty or not.
            if self.is_empty(prompt) is True:
                # if it's empty and our prompt is for hours,
                # set current, if applicable.
                if prompt == 'hours' and int(self.config.default_hours) > 0:
                    current = self.config.default_hours

                # set-up kwargs to be passed to ``prompt_for``
                kwargs = dict(
                    default='0',
                    current=current,
                    display_multiple_header=not multiple_heading_displayed,
                    display_single_header=not single_heading_displayed
                )

                # prompt the user for input, and check the result.
                with self.prompt_for(prompt, **kwargs) as result:
                    logger.debug(
                        'result from prompt: {}, key: {}: {}'.format(
                            prompt, self.key_for_prompt(prompt), result)
                    )

                    # update ``self`` with the value of the result.
                    self.update(
                        {self.key_for_prompt(prompt): result.value}
                    )
                    # set which/if heading's were displayed.
                    multiple_heading_displayed = \
                        result.multiple_heading_displayed
                    single_heading_displayed = \
                        result.single_heading_displayed
        # show the changes that have been applied if ``debug`` is True.
        if self.config.debug is True:
            with self.ctx(strict=False) as ctx:
                logger.debug(
                    'ctx after prompts: {}, hours: {}, rate: {}'.format(
                        ctx, self._hours(), self.rate)
                )

    def prompt_all(self) -> None:
        """Prompt the user for all input's, also showing the current value, and
        add the values to this instance appropriately.

        """

        if self.config.debug is True:
            with self.ctx() as ctx:
                logger.debug(
                    'before prompts: {}, hours: {}, rate: {}'.format(
                        ctx, self._hours(), self.rate)
                )

        multiple_heading_displayed = False
        single_heading_displayed = False

        for prompt in self._prompts:
            # set current value up appropriately.
            if prompt == 'cost':
                current = self._costs()
            elif prompt == 'rate':
                current = self.rate
            elif prompt == 'hours':
                current = self._hours()
            else:
                with self.ctx(strict=False) as ctx:
                    current = getattr(ctx, prompt, None)

            # set kwargs to pass to ``prompt_for`` method.
            kwargs = dict(
                default='0',
                current=current,
                display_multiple_header=not multiple_heading_displayed,
                display_single_header=not single_heading_displayed
            )

            # prompt the user for input and use the result.
            with self.prompt_for(prompt, **kwargs) as result:
                # update self with the value.
                self.update({self.key_for_prompt(prompt): result.value})
                # set which/if we displayed any headings
                multiple_heading_displayed = \
                    result.multiple_heading_displayed
                single_heading_displayed = \
                    result.single_heading_displayed

        if self.config.debug is True:
            with self.ctx() as ctx:
                logger.debug(
                    'after prompts: {}, hours: {}, rate: {}'.format(
                        ctx, self._hours(), self.rate)
                )
