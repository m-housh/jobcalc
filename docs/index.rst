.. jobcalc documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jobcalc's documentation!
======================================

.. image:: https://img.shields.io/travis/m-housh/jobcalc.svg
        :target: https://travis-ci.org/m-housh/jobcalc

.. image:: https://coveralls.io/repos/github/m-housh/jobcalc/badge.svg?branch=master
        :target: https://coveralls.io/github/m-housh/jobcalc?branch=master

.. image:: https://readthedocs.org/projects/jobcalc/badge/?version=latest
        :target: http://jobcalc.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status



**jobcalc** aims to be a simple, but effective way at quickly calculating
job costs, using any combination of the following items.

* percentage profit margin
* hours and hourly rate
* percentage discounts
* monetary deductions

This project started one weekend, as I thought that I wish I had a simple, 
elegant, and flexible way to quickly calculate a job cost while still in
a terminal session, it grew from there to be extensible through custom
**Formatter's** to be able to be used in more than just a command line
application

Because of the use of type-hints, **python 3.5** or above are the only supported
versions for this package.  Sorry for this limitation, but this package is
also used in conjunction with a larger private project, where the type-hints
are handy.

* Free software: MIT license
* Documentation: https://jobcalc.readthedocs.io.
* Repo: https://github.com/m-housh/jobcalc

Contents:

.. toctree::
   :maxdepth: 2

   readme
   installation
   usage
   config
   screenshots
   api
   contributing
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
