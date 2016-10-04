============
Python Usage
============
.. module:: jobcalc

**This part of the documentation is not yet complete.**


When using these utils in your python code, the best place to start is
the :py:class:`jobcalc.Calculator` or :py:class:`jobcalc.BaseCalculator`
classes, depending on your use case.

Base Calculator
---------------

The :py:class:`~jobcalc.BaseCalculator` class is basic and does not support
using formatters to ``render`` the output.  It also does not support ``hours``
and ``rate`` or using any of the ``config`` classes, but can be useful if you 
have your own means of calculating the ``costs`` for a job.

.. seealso:: 
    :py:class:`jobcalc.BaseCalculator` for specific documentation.

Usage::
    from jobcalc import BaseCalculator



Calculator
----------

The :py:class:`~jobcalc.Calculator` class supports ``hours`` and ``rate``, to
help in calculating the ``costs`` for a job. It also supports adding
``formatters`` in order to ``render`` the output.

.. seealso::
    :py:class:`jobcalc.Calculator` class for specific documentation and
    :py:mod:`jobcalc.formatters` module for documentation on formatters.

Usage::

    from jobcalc import Calculator


Formatters
----------

Formatters are what are used with the :py:class:`~jobcalc.Calculator` class to
``render`` output.  There are several basic formatters in the
:py:mod:`jobcalc.formatters` module, all of which pertain to the command line
interface for this package.  However by extending the
:py:class:`~jobcalc.BaseFormatter` class, one can render the output in any
format they like.

.. seealso:: :py:mod:`jobcalc.formatters` module.

Creating a Basic Formatter::

    from jobcalc import BaseFormater, BaseCalculator

    class Basic(BaseFormatter):

        @staticmethod
        def render(calculator) -> str:
            if not isinstance(calculator, BaseCalculator):
                raise TypeError(
                    '{} should be a BaseCalculator or sub-class'.format(
                        calculator))

            return calculator.total().formatted_string()

