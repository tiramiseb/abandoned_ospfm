#########################
OSPFM global architecture
#########################

OSPFM is  a RESTful  pplication serving information  and answering  to requests
in the JSON format.

OSPFM may be divided in differents subparts.

List of subparts
================

* ``automation``: automatic transformations or creations
* ``core``: core data, not belonging to any other part
* ``debt``: debts between users
* ``envelope``: envelope-oriented budgeting
* ``preconfigured``: preset transactions for easy add
* ``programmed``: programmed transactions
* ``refund``: refunds management (like social protection reimbursements)
* ``transaction``: transactions, accounts, categories

Choice of framework
===================

At first, the name "OSPFM" represented all parts of the project : the database,
the back-end, the interfaces.  And everything would have been made with Django.
But this  choice  was too  restrictive.  That's why  the name "OSPFM"  now only
applies to the  back-end server, and  Django is not used for  this part because
many of its features are not used in the back-end: templates, etc.

Flask has been  chosen because it is lightweight;  and, of course,  because its
programming language is Python.

SQL schema
==========

The database SQL  schema is described in the  ``ospfm-sql-schema.dia`` Dia file
(``ospfm-sql-schema.png`` for an easily readable image).
