search_in_files
===============

This is a tool for searching text in files.

- It is smart enough to run in parallel on multi-core computers and run mode on single-core computers
- Handle utf-8 text files
- Handle big files as well
- It is fast ;)

For more information see:
https://github.com/danielgatis/search_in_files/blob/master/notebooks/search_in_files.ipynb

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
