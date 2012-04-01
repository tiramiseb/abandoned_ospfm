#########################
OSPFM global architecture
#########################

OSPFM is divided into multiple different subparts, implemented as Django
applications.

The following schema explains interaction between them::

                    +-----------------------+
                    | +-----------------------+
                    | | +-----------------------+
                    | | |                       |
                    +-| | back-end applications |
                      +-|                       |
                        +-----------------------+

                      /              |            \
                     /               |             \
                    /                |              \
                   /                 |               \
 +----------------------+ +--------------------+ +---------------------+
 |                      | |                    | |  subscription and   |
 | mobile web interface | | rich web interface | | billing application |
 |                      | |                    | |  (not Open Source)  |
 +----------------------+ +--------------------+ +---------------------+

List of applications
====================

Back-end applications
---------------------

Data storage and manipulation is done in Django applications.

These applications are:

* ``ospfm_automation``: automatic transformations or creations
* ``ospfm_core``: core data, not belonging to any other part
* ``ospfm_debt``: debts between users
* ``ospfm_envelope``: envelope-oriented budgeting
* ``ospfm_programmed``: programmed transactions
* ``ospfm_refund``: refunds management (like social protection reimbursements)
* ``ospfm_transaction``: transactions, accounts, categories

Rich web interface
------------------

The rich web interface is oriented toward users on computers (and maybe on
tablets).

Mobile web interface
--------------------

The mobile web interface is optimized for smartphones (and maybe tablets).

Subscription and billing application
------------------------------------

A subscription and billing application should manage users and their
authorizations. This is not a part of OSPFM, it is not distributed as an
Open Source product.

Django models
=============

Django models for OSPFM are described in the ``ospfm-django-models-schema.dia``
Dia file (``ospfm-django-models-schema.png`` for an easily readable image).




