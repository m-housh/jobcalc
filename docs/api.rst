=======
API
=======

.. module:: jobcalc

The public interface for ``jobcalc``.


Core
-----

The following items are found in the ``jobcalc.core`` module, but
are also loaded into the ``jobcalc`` namespace.

.. autoclass:: BaseCalculator
    :members:

.. autoclass:: Calculator
    :members:

.. autoclass:: TerminalCalculator
    :members:

.. autofunction:: calculate

.. autoclass:: Context

.. autoclass:: PromptResponse

The following iterms are not imported into the ``jobcalc`` namespace, and
need to be imported directly from ``jobcalc.core``.

.. autoclass:: jobcalc.core.ColorKey

.. autoattribute:: jobcalc.core.DEFAULT_COLOR_KEY

Config
-------

The following items are found in the ``jobcalc.config`` module, but
are also loaded into the ``jobcalc`` namespace.

.. autoclass:: Config
    :members:

.. autoclass:: TerminalConfig
    :members:

The following items are not imported into the ``jobcalc`` namespace, and
need to be imported directly from ``jobcalc.config``.

.. autodata:: jobcalc.config.ENV_PREFIX

.. autodata:: jobcalc.config.CURRENCY_FORMAT

.. autodata:: jobcalc.config.LOCALE

.. autodata:: jobcalc.config.env_string


Utils
--------

The following items are found in the ``jobcalc.utils`` module, but
are also loaded into the ``jobcalc`` namespace.

.. autofunction:: bool_from_env_string

.. autofunction:: ensure_callback

.. autofunction:: dict_from_env_string

.. autofunction:: parse_input_string

.. autofunction:: flatten

.. autofunction:: colorize

Exceptions
----------

The following items can be found in the ``jobcalc.exceptions`` module,
but are also loaded into the ``jobcalc`` namespace.

.. autoexception:: JobCalcError

.. autoexception:: InvalidEnvString

.. autoexception:: EnvDictNotFound

.. autoexception:: NotCallableError

.. autoexception:: PercentageOutOfRange

.. autoexception:: NotIterableError

.. autoexception:: InvalidFormatter

.. autoexception:: HourlyRateError


Formatters
----------

The following items can be found in the ``jobcalc.formatters`` module, but
are also loaded into default ``jobcalc`` namespace.

.. autoclass:: BaseFormatter
    :members:

.. autoclass:: BasicFormatter
    :members:

.. autoclass:: TerminalFormatter
    :members:

.. autoclass:: FormulaFormatter
    :members:

The following items can be imported from the ``jobcalc.formatters`` module.


.. autoclass:: jobcalc.formatters.ColorContext

.. autoclass:: jobcalc.formatters.TotaledContext

.. autodata:: jobcalc.formatters.DEFAULT_COLORS

Types
------

The following items can be imported from ``jobcalc.types`` module.

.. autoclass:: jobcalc.types.Percentage
    :members:

.. autoclass:: jobcalc.types.Currency
    :members:

.. autoclass:: jobcalc.types.BaseCurrencyType
    :members:

.. autoclass:: jobcalc.types.BasePercentageType
    :members:

.. autoclass:: jobcalc.types.DeductionsType
    :members:

.. autoclass:: jobcalc.types.MarginsType
    :members:

.. autoclass:: jobcalc.types.DiscountsType
    :members:

.. autoclass:: jobcalc.types.CostsType
    :members:

.. autoclass:: jobcalc.types.HoursType
    :members:

.. autofunction:: jobcalc.types.parse_input_value

.. autofunction:: jobcalc.types.check_env_dict

