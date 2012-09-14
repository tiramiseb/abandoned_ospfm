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

::

    GET /currencies

Response
--------

Example::

    {
        "status": 200,
        "response": [
            {
                "isocode": "AED",
                "name": "United Arab Emirates dirham"
            },
            {
                "isocode": "AFN",
                "name": "Afghan afghani"
            },
        [...]
    }

Create
======

Create a new user-defined currency

Request
-------

::

    POST /currencies

Data
----

* ``isocode``: isocode of the new currency (max 5 chars, not already used)
* ``symbol``: symbol of the new currency (max 5 chars)
* ``name``: name of the new currency (max 50 chars)
* ``rate``: rate of the new currency against the user's preferred currency

Response
--------

::

    {
        "status": 200,
        "response": {
            "owner": "<username>",
            "isocode": "<isocode>",
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

::

    GET /currencies/<isocode>

* ``<isocode>``: isocode of the currency to read

Response
--------

For global currencies::

    {
        "status": 200,
        "response": {
            "isocode": "<isocode of the currency>",
            "symbol": "<symbol of the currency>",
            "name": "<name of the currency>"
        }
    }

For user-defined currencies::

    {
        "status": 200,
        "response": {
            "owner": "<username>",
            "isocode": "<isocode>",
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

::

    PUT /currencies/<isocode>

* ``<isocode>``: isocode of the currency to update

Data
----

All are optional

* ``isocode``: new isocode of the currency (max 5 chars, not already used)
* ``symbol``: new symbol of the currency (max 5 chars),
* ``name``: new name of the currency (max 50 chars)
* ``rate``: new rate of the currency against the user's preferred currency

Response
--------

::

    {
        "status": 200,
        "response": {
            "owner": "<username>",
            "isocode": "<isocode>",
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

::

    DELETE /currencies/<isocode>

* ``<isocode>``: isocode of the currency to delete

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

::

    GET /currencies/<isocode1>/rate/<isocode2>

* ``<isocode1>``: isocode of the "from" currency
* ``<isocode2>``: isocode of the "to" currency

Response
--------

::

    {
        "status": 200,
        "response": <rate>
    }
