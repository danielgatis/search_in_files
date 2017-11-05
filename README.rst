search_in_files
===============

This is a tool for search text in files.

- It is smart enough to run in parallel on multi-core computers and run mode on single-core computers
- Handles different types character encodings
- Handles big files as well
- It is fast ;)


.. figure:: https://github.com/danielgatis/search_in_files/blob/master/demo.gif?raw=true
   :alt: demo
   

For more information see `here <:: https://github.com/danielgatis/search_in_files/blob/master/notebooks/search_in_files.ipynb>`_.

How to install
==============

::

    pip install search_in_files

How to run the tests
====================

::

    python -m search_in_files.search_test

How to run
==========

::

    search_in_files <pattern> <folder>
