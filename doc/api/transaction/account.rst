########################
OSPFM REST API : Account
########################

This document details the OSPFM REST API for Account requests.

Restrictions
============

A user can only see his own accounts.
A user can only create, update or delete his own accounts.

List
====

List all user's accounts

Request
-------

::

    GET /accounts

Response
--------

::

    {
        "status": 200,
        "response": {
            "accounts": [
                {
                    "start_balance": <start balance>,
                    "currency": "<currency isocode>",
                    "id": <account unique id>,
                    "name": "<account name>",
                    "balance": <account balance>
                },
                [...]
            ],
            "total": {
                "currency": "<currency for the total balance>",
                "balance": <total balance>
            }
        }
    }

Create
======

Create a new account

Request
-------

::

    POST /accounts

Data
----

* ``name``: name of the new account (max 50 chars)
* ``currency``: isocode of the currency of the account
* ``start_balance``: start balance of the account

Response
--------

::

    {
        "status": 200,
        "response": {
                "start_balance": <start balance>,
                "currency": "<currency isocode>",
                "id": <account unique id>,
                "name": "<account name>"
        }
    }

Read
====

Read an account

Request
-------

::

    GET /accounts/<id>

* ``<isocode>``: unique id of the account

Response
--------

::

    {
        "status": 200,
        "response": {
                "start_balance": <start balance>,
                "currency": "<currency isocode>",
                "id": <account unique id>,
                "name": "<account name>",
                "balance": <account balance>
        }
    }

Update
======

Update an account

Request
-------

::

    PUT /account/<id>

* ``<id>``: unique id of the account

Data
----

All are optional

* ``name``: new name of the new account (max 50 chars)
* ``currency``: isocode of the new currency of the account (an account's
  currency may only be changed if there are no transaction in the account)
* ``start_balance``: new start balance of the account

Response
--------

::

    {
        "status": 200,
        "response": {
                "start_balance": <start balance>,
                "currency": "<currency isocode>",
                "id": <account unique id>,
                "name": "<account name>",
                "balance": <account balance>
        }
    }

Delete
======

Delete an account.

Consequences on other stuff (especially transactions) will be detailed later.

Request
-------

::

    DELETE /accounts/<id>

* ``<id>``: unique id of the account

Response
--------

::

    {
        "status": 200,
        "response": "OK Deleted"
    }
