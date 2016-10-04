===============================
jobcalc
===============================


.. image:: https://img.shields.io/travis/m-housh/jobcalc.svg
        :target: https://travis-ci.org/m-housh/jobcalc

.. image:: https://coveralls.io/repos/github/m-housh/jobcalc/badge.svg?branch=master
        :target: https://coveralls.io/github/m-housh/jobcalc?branch=master

Job calculator utilities and command line application.  Currently only
supports python 3.5 or above, because of the use of type-hints.



* Free software: MIT license
* Documentation: https://jobcalc.readthedocs.io.


Features
--------

* Configurable calculations for job costing.
* Command Line Interface
* Profit Margin calculation
* Supports Percentage Discounts
* Supports Hours and Hourly rate calculation's
* Supports Monetary Deductions

Todo's
------

* Work on finalizing the docs.
* Add more examples.
* Add Docker documentation.
* Add option to output to a file.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.
This package uses Click_ for the command line interface, terminaltables_ for
the Ascii table output, along with colorclass_ for color strings, wrapt_ for
better decorators, and babel_ for currency formatting.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Click: http://click.pocoo.org/
.. _terminaltables: https://pypi.python.org/pypi/terminaltables/3.0.0
.. _colorclass: https://pypi.python.org/pypi/colorclass
.. _babel: http://babel.pocoo.org/en/latest/
.. _wrapt: http://wrapt.readthedocs.io/en/latest/

