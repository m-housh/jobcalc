=============
Configuration
=============
.. module:: jobcalc

There are two ways to configure a calculation, through environment variables,
or through a yaml config file.  Both methods can be used in conjuction with
another, however a value inside of the config file will override a value in
the environment.

.. seealso:: 
    :py:mod:`jobcalc.config` module and :py:class:`jobcalc.config.Config`

Variables
---------

All environment variables are prefixed with ``JOBCALC_``, with one exception,
debug mode can be set by either ``JOBCALC_DEBUG`` or ``DEBUG`` in the
environment.

**Below is description of each variable and what it does**  

*Environment Variable (left), Yaml Variable (right)*

* **JOBCALC_DEBUG**, **debug**
    Puts calculation into debug mode for verbose logging.

* **JOBCALC_CURRENCY_FORMAT**, **currency_format**
    Sets format for currency string's.  Should be set to a valid format used
    by ``babel.numbers.format_currency``.  Defaults to ``USD``.

* **JOBCALC_LOCALE**, **locale**
    Sets locale for currency string's.  Should be set to a valid locale used by
    ``babel.numbers.format_currency``.  Defaults to ``en_US``.

* **JOBCALC_SEPERATOR**, **seperator**
    Sets seperator to be used to seperate items in a string.  
    Defaults to ``;``.

* **JOBCALC_DIVIDER**, **divider**
    Sets divider to be used to divide key, value pairs in a string. Defaults
    to ``:``.

* **JOBCALC_RATE**, **rate**
    An hourly rate to be used in the calculations. Defaults to ``0``.

* **JOBCALC_DEFAULT_HOURS**, **default_hours**
    Hours to _always_ use in a calculation.  Defaults to ``0``.

* **JOBCALC_MARGINS**, **margins**
    A dict like string used to have **named** margins that can be used.
    Margins get converted to :py:class:`~jobcalc.param_types.Percentage`'s.
    An example would be *'fifty:50;forty:40'*.  And when setting a value for
    a margin then you can use *'fifty'* for a 50% margin.  The key and value
    neead to be seperated by the **JOBCALC_DIVIDER** and the items need to be
    seperated by the **JOBCALC_SEPERATOR**.

* **JOBCALC_DISCOUNTS**, **discounts**
    A dict like string used to have **named** discounts that can be used.
    Discounts get converted to :py:class:`~jobcalc.param_types.Percentage`'s. 
    An example would be *'standard:5;deluxe:10'*. The key and value 
    need to be seperated by the  **JOBCALC_DIVIDER** and the items need to be 
    seperated by the **JOBCALC_SEPERATOR**.

* **JOBCALC_DEDUCTIONS**, **deductions**
    A dict like string used to have **named** deductions that can be used.
    Deductions get converted to :py:class:`~jobcalc.param_types.Currency`'s.
    An example would be *'one:100;two:200'*. The key and value 
    need to be seperated by the  **JOBCALC_DIVIDER** and the items need to be 
    seperated by the **JOBCALC_SEPERATOR**.

.. note::
    It is also possible to set a default value for the ``dict`` like strings.
    by including the key ``'default'`` inside the string, it's value can either
    be another key inside the dict string or an actual value that will get
    converted to the appropriate type.


Terminal Config Environment Variables
-------------------------------------

The following variables are relevant to :py:class:`~.config.TerminalConfig`.
Most of these varibles are boolean strings, any of the following values will
be determined as ``True``.  

* 'true' in any combination of upper or lowercase (ex. 'TrUE' will be ``True``).
* '1'

Anything else is ``False``.

.. seealso:: :py:class:`jobcalc.config.TerminalConfig`

* **JOBCALC_PROMPT**, **prompt**
    A bool string that if determined to be ``True`` and the ``job-calc`` command
    is called from the terminal without a sub-command, then we will invoke
    the ``prompt-all`` sub-command.  If ``False`` then the help doc will be
    shown.  Default is ``False``.

* **JOBCALC_SUPPRESS**, **suppress**
    A bool string that if determined to be ``True`` will suppress the detailed
    table output on all sub-commands.  Default is ``False``.

* **JOBCALC_FORMULA**, **formula**
    A bool string that if determined to be ``True`` will show the formula 
    string on any sub-commands.  Default is ``False``.

* **JOBCALC_ALLOW_EMPTY**, **allow_empty**
    A bool string that if determined to be ``True`` will not prompt the user
    for values that are determined to be empty.  Default is ``False``.

* **JOBCALC_PROMPT_SEPERATOR**, **prompt_seperator**
    A string that is used to seperate multiple items during a prompt.
    Defaults to an empty space ``' '``.  This allows multiple values to be 
    passed in at a prompt.

.. _yaml-config-example:

Yaml Config Example
-------------------

The following is an example yaml file that can be used to configure
a calculation.

config.yml::

    discounts:
        standard: 5
        deluxe: 10
        premium: 15
        default: deluxe
    rate: 20
    formula: true
    allow_empty: true

.. command-output::
    job-calc -c config.yml --margin 50 --hours 10 table 123

As you can see in the above, our discount get's set to the ``default`` key.
Which maps back to ``deluxe`` which is 10%.  Our ``hours`` get multiplied by
the ``rate`` set in the config.  And the output also show's the formula for
the calculation.

Environment Config Example
--------------------------

The following is the same as the :ref:`yaml-config-example` only using 
environment variables instead.

.. command-output::
    export JOBCALC_DISCOUNTS='standard:5;deluxe:10;premium:15;default:deluxe' &&
    \
    export JOBCALC_RATE=20 && \
    export JOBCALC_FORMULA=true && \
    export JOBCALC_ALLOW_EMPTY=true && \
    job-calc --margin 50 --hours 10 table 123
    :shell:
