========================
Command Line Usage
========================

Set the margin(s), discount(s), hour(s), rate.  

Call a sub-command, which chooses a formatter to format the output correctly.  

Certain options can be set after the sub-command (hour(s), rate, deduction(s)) 
All arguments after sub-command options are costs (material(s) etc. for the job 
calculation).


Basic Usage
-----------

.. command-output:: 
    job-calc --allow-empty --margin 50 --discount 10 total --hours '20;10' \
        --rate 20 123 456
        

In the above example ``job-calc`` is the main command, ``margin``,
``allow-empty``, ``discount`` are options for the main command, ``total`` is 
the sub-command, ``hours`` and ``rate`` are options for the sub-command, 
``123 456`` are arguments (costs).

.. note::
    If passing multiple values to **options** on the command line, then they 
    should be wrapped in quotes to avoid errors, like the **hours** above.


Show help
---------

    .. command-output:: job-calc --help


Show sub-command help
---------------------

    .. command-output:: job-calc formula --help


Options
-------

These are options that are passed after the main command ``job-calc`` and
before any sub-commands.  See `Basic Usage`_, for more details. 


* -a / --allow-empty  
    If this option is set then we will not prompt for empty values.  If not
    set, then any values that are empty will be prompted for before showing
    the formatted output.

* -m / --margin  
    The value to use as the profit margin for the calculation.  This can
    be a multiple value seperated by a seperator (default is ';').

* -d / --discount  
    A percentage discount to be applied to the calculation. This can
    be a multiple value seperated by a seperator (default is ';').

* -h / --hours  
    The hours for the job.  This can be a multiple value seperated by a 
    seperator (default is ';').

* -r / --rate  
    The hourly rate to be used for the job.  This is a single value only.

* -c / --config
    Path to a yaml file to use as the config for a calculator.

To avoid having to use the full option name the following options can be set
after the sub-command.

* -d / --deduction  
    This is a monetary deduction to subtract from the total. This can
    be a multiple value seperated by a seperator (default is ';').

* -h / --hours  
    The hours for the job.  This can be a multiple value seperated by a 
    seperator (default is ';').

* -r / --rate  
    The hourly rate to be used for the job.  This is a single value only.

Sub-Commands
------------

These are sub-commands that are called based on the format you would like
the output to be in.  The options for these come after the sub-command has
been declared on the command line.  See `Basic Usage`_, for more details.


:formula:  Show a formatted string of the formula used for the calculation.

    :options:  

    * -d / --deduction  
        This is a monetary deduction to subtract from the total. This can
        be a multiple value seperated by a seperator (default is ';').
    
    * -h / --hours  
        The hours for the job.  This can be a multiple value seperated by a 
        seperator (default is ';').
    
    * -r / --rate  
        The hourly rate to be used for the job.  This is a single value only.

    * -t / --table  
        Show the detailed table along with the formula.

:Example:

.. image:: _static/formula_output.png

----

:table: Show a detailed table of the calculation.

    :options:  

    * -d / --deduction  
        This is a monetary deduction to subtract from the total. This can
        be a multiple value seperated by a seperator (default is ';').
    
    * -h / --hours  
        The hours for the job.  This can be a multiple value seperated by a 
        seperator (default is ';').
    
    * -r / --rate  
        The hourly rate to be used for the job.  This is a single value only.

    * -f / --formula
            Show the formatted formula along with the table.

:Example:

.. image:: _static/table_output.png

-----

:total: Show just the total of the calculation.

    :options:  

    * -d / --deduction  
            This is a monetary deduction to subtract from the total. This can
            be a multiple value seperated by a seperator (default is ';').
        
    * -h / --hours  
            The hours for the job.  This can be a multiple value seperated by a 
            seperator (default is ';').
        
    * -r / --rate  
            The hourly rate to be used for the job.  This is a single value only.

:Example:

.. image:: _static/total_output.png

----

:prompt-all:  Prompt user for all the inputs for a calculation.  
              
This can also be set as the default command to run, if no sub-commands are 
passed to the ``job-calc`` command, by setting environment 
variable ``JOBCALC_PROMPT`` to something that parses to ``True`` 
('TRUE', 'true', 'TrUe', '1', 1).  If no options are passed to 
this command, then we just show the total.

    :options:

    * -f / --formula
        Show the formatted formula.

    * -t / --table  
        Show the detailed table.

:Example:

.. image:: _static/prompt_all_output.png

----

Using Named Parameter Options
-----------------------------

You can use environment variables to allow named options to be used on the
command line.  We parse an environment variable into a dict of key, value
pairs, where the keys are the named parameter you would like to use on the
command line, and the value will be what is returned by that key and parsed
into the correct type.

These named parameters can be used in prompts or mixed and matched with
other values that are not a named parameter.

While everyone's use case may be different a good example would be having
customers that have a different discount based on a type of service you
provide for them, a loyalty discount.  So say customers fit into one of the
three categories (besides getting no discount).

Discounts:
    * standard:  We want a 5% discount.
    * deluxe:  We want a 10% discount.
    * premium:  We want a 15% discount.

Set the environment variable.

.. code-block:: bash

    $ export JOBCALC_DISCOUNTS='standard:5;deluxe:10;premium:15'

Run the command using the named option (deluxe) for discount.

.. code-block:: bash

    $ job-calc --allow-empty --margin 50 --discount deluxe table \
        --rate 20 --hours '20;10' 123 456

Output.

.. program-output::
    export JOBCALC_DISCOUNTS='standard:5;deluxe:10;premium:15' && \
        job-calc --allow-empty --margin 50 --discount deluxe table \
            --rate 20 --hours '20;10' 123 456
    :shell:

Mixing with other values works as well.

.. code-block:: bash

    $ job-calc --allow-empty --margin 50 --discount 'deluxe; 3' table \
        --rate 20 --hours 10 123 456 789


Output.

.. program-output::
    export JOBCALC_DISCOUNTS='standard:5;deluxe:10;premium:15' && \
        job-calc --allow-empty --margin 50 --discount 'deluxe;3' table \
            --rate 20 --hours 10 123 456 789
    :shell:
