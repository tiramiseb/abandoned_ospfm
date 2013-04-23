###################
OSPFM global README
###################

*OSPFM* stands for *Open Source Personal Finance Management server*.

OSPFM is the foundation for a future Software-as-a-Service finance application,
named everCount.

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

Prerequisite
============

Short list of prerequisite for OSPFM:

- Python 2.7 or newer (some parts will not work with Python up to 2.6)
- Flask (Debian package ``python-flask``)
- SQLAlchemy 0.7 or newer (Debian package ``python-sqlalchemy``)
- Flask-SQLAlchemy (``pip install flask-sqlalchemy``)
- SimpleJSON 2.6 or newer (Debian package ``python-simplejson``)
- a SQL database system compatible with SQLAlchemy
