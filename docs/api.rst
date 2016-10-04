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
    :noindex:

.. autoclass:: Calculator
    :members:
    :noindex:

.. autoclass:: TerminalCalculator
    :members:
    :noindex:

.. autofunction:: calculate
    :noindex:

.. autoclass:: Context
    :noindex:

.. autoclass:: PromptResponse
    :noindex:

The following iterms are not imported into the ``jobcalc`` namespace, and
need to be imported directly from ``jobcalc.core``.

.. autoclass:: jobcalc.core.ColorKey
    :noindex:

.. autoattribute:: jobcalc.core.DEFAULT_COLOR_KEY
    :noindex:

.. _config:

Config
-------

The following items are found in the ``jobcalc.config`` module, but
are also loaded into the ``jobcalc`` namespace.

.. autoclass:: Config
    :members:
    :noindex:

.. autoclass:: TerminalConfig
    :members:
    :noindex:

The following items are not imported into the ``jobcalc`` namespace, and
need to be imported directly from ``jobcalc.config``.

.. autodata:: jobcalc.config.ENV_PREFIX
    :noindex:

.. autodata:: jobcalc.config.CURRENCY_FORMAT
    :noindex:

.. autodata:: jobcalc.config.LOCALE
    :noindex:

.. autodata:: jobcalc.config.env_strings
    :noindex:


Utils
--------

The following items are found in the ``jobcalc.utils`` module, but
are also loaded into the ``jobcalc`` namespace.

.. autofunction:: bool_from_env_string
    :noindex:

.. autofunction:: ensure_callback
    :noindex:

.. autofunction:: dict_from_env_string
    :noindex:

.. autofunction:: parse_input_string
    :noindex:

.. autofunction:: flatten
    :noindex:

.. autofunction:: colorize
    :noindex:

Exceptions
----------

The following items can be found in the ``jobcalc.exceptions`` module,
but are also loaded into the ``jobcalc`` namespace.

.. autoexception:: JobCalcError
    :noindex:

.. autoexception:: InvalidEnvString
    :noindex:

.. autoexception:: EnvDictNotFound
    :noindex:

.. autoexception:: NotCallableError
    :noindex:

.. autoexception:: PercentageOutOfRange
    :noindex:

.. autoexception:: NotIterableError
    :noindex:

.. autoexception:: InvalidFormatter
    :noindex:

.. autoexception:: HourlyRateError
    :noindex:


Formatters
----------

The following items can be found in the ``jobcalc.formatters`` module, but
are also loaded into default ``jobcalc`` namespace.

.. autoclass:: BaseFormatter
    :members:
    :noindex:

.. autoclass:: BasicFormatter
    :members:
    :noindex:

.. autoclass:: TerminalFormatter
    :members:
    :noindex:

.. autoclass:: FormulaFormatter
    :members:
    :noindex:

The following items can be imported from the ``jobcalc.formatters`` module.


.. autoclass:: jobcalc.formatters.ColorContext
    :noindex:

.. autoclass:: jobcalc.formatters.TotaledContext
    :noindex:

.. autodata:: jobcalc.formatters.DEFAULT_COLORS
    :noindex:

Param Types
-----------

The following items can be imported from ``jobcalc.param_types`` module.

.. autoclass:: jobcalc.param_types.Percentage
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.Currency
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.BaseCurrencyType
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.BasePercentageType
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.DeductionsType
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.MarginsType
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.DiscountsType
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.CostsType
    :members:
    :noindex:

.. autoclass:: jobcalc.param_types.HoursType
    :members:
    :noindex:

.. autofunction:: jobcalc.param_types.parse_input_value
    :noindex:

.. autofunction:: jobcalc.param_types.check_env_dict
    :noindex:

