#########################
OSPFM REST API : Currency
#########################

This document details the OSPFM REST API for Currency requests.

Restrictions
============

A user can only see his own currencies and globally-defined currencies.
A user can only create, update or delete his own user-defined currencies.

List
====

List all currencies available to the user

Request
-------

``GET /currencies``

Response
--------

Example::

    {
        "status": 200,
        "response": [
            {
                "symbol": "AED",
                "name": "United Arab Emirates dirham"
            },
            {
                "symbol": "AFN",
                "name": "Afghan afghani"
            },
        [...]
    }

Create
======

Create a new user-defined currency

Request
-------

``POST /currencies``

Data
----

* ``symbol``: symbol of the new currency (max 5 chars, not already used)
* ``name``: name of the new currency (max 50 chars)
* ``rate``: rate of the new currency against the user's preferred currency

Response
--------

::

    {
        "status": 200,
        "response": {
            "owner": "<username>",
            "symbol": "<symbol>",
            "name": "<currency name>",
            "rate": <currency rate>
        }
    }

Read
====

Read a currency

Request
-------

``GET /currencies/<symbol>``

* ``<symbol>``: symbol of the currency to read

Response
--------

For global currencies::

    {
        "status": 200,
        "response": {
            "symbol": "<symbol of the currency>",
            "name": "<name of the currency>"
        }
    }

For user-defined currencies::

    {
        "status": 200,
        "response": {
            "owner": "<username>",
            "symbol": "<symbol>",
            "name": "<currency name>",
            "rate": <currency rate>
        }
    }

Update
======

Update a user-defined currency

Request
-------

``PUT /currencies/<symbol>``

* ``<symbol>``: symbol of the currency to update

Data
----

All are optional

* ``symbol``: new symbol of the currency (max 5 chars, not already used)
* ``name``: new name of the currency (max 50 chars)
* ``rate``: new rate of the currency against the user's preferred currency

Response
--------

::

    {
        "status": 200,
        "response": {
            "owner": "<username>",
            "symbol": "<symbol>",
            "name": "<currency name>",
            "rate": <currency rate>
        }
    }

Delete
======

Delete a user-defined currency.
Only unused currencies can be deleted.

Request
-------

``DELETE /currencies/<symbol>``

* ``<symbol>``: symbol of the currency to delete

Response
--------

::

    {
        "status": 200,
        "response": "OK Deleted"
    }

Exchange rate
=============

Get exchange rate from a currency to another currency

Request
-------

``GET /currencies/<symbol1>/rate/<symbol2>``

* ``<symbol1>``: symbol of the "from" currency
* ``<symbol2>``: symbol of the "to" currency

Response
--------

::

    {
        "status": 200,
        "response": <rate>
    }
