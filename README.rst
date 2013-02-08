###################
OSPFM global README
###################

*OSPFM* stands for *Open Source Personal Finance Management server*.

OSPFM is the foundation for a future Software-as-a-Service finance application,
named everCount.

*OSPFM* official website is http://tiramiseb.github.com/ospfm.

Documentation as HTML
=====================

To convert  all documentation  to HTML,  you need the  docutils tool  (from the
python-docutils  package  in some  Linux  distributions).  Simply  execute  the
``docs-to-html.sh`` script in the project's root directory. Every ``.rst`` file
will then have a HTML equivalent.

When you read them online on the GitHub website,  these files are automatically
converted.

Manifesto
=========

To  understand  the motivation  behind  OSPFM,  please  read  the  manifesto in
``MANIFESTO.rst``.

License
=======

OSPFM  is published  under the  terms of the  GNU Affero General Public License
version 3.

What exactly is OSPFM ?
-----------------------

OSPFM is  a multi-users  personal finance  "backend" application,  hosting  the
"intelligence" for any number of frontend client applications.

User management is not a part of OSPFM.
The frontend clients don't have to be licensed under the AGPL license.
