#########################
OSPFM REST API : Category
#########################

This document details the OSPFM REST API for Category requests.

Restrictions
============

A user can only see his own categories.
A user can only create, update or delete his own categories.

List
====

List all user's categories

Request
-------

::

    GET /categories

Response
--------

Example::

{
    "status": 200,
    "response": [
        {
            "children": [
                {
                    "id": 8,
                    "currency": "EUR",
                    "name": "Fuel"
                },
                {
                    "id": 7,
                    "currency": "EUR",
                    "name": "Insurance"
                }
            ],
            "id": 1,
            "currency": "EUR",
            "name": "Car"
        },
        {
            "children": [
                {
                    "id": 10,
                    "currency": "EUR",
                    "name": "Danceclub"
                }
            ],
            "id": 3,
            "currency": "EUR",
            "name": "Fun"
        },
        {
            "children": [
                {
                    "children": [
                        {
                            "id": 14,
                            "currency": "EUR",
                            "name": "Electricity"
                        },
                        {
                            "id": 15,
                            "currency": "EUR",
                            "name": "Internet access"
                        }
                    ],
                    "id": 9,
                    "currency": "EUR",
                    "name": "Invoices"
                }
            ],
            "id": 2,
            "currency": "EUR",
            "name": "House"
        }
    ]
}

Create
======

Create a new category

Request
-------

::

    POST /categories

Data
----

* ``name``: name of the new category (max 50 chars)
* ``parent``: unique id of the parent category (optional)
* ``currency``: default currency for this category

Response
--------

If no parent is defined::

{
    "status": 200,
    "response": {
        "id": <new category unique id>,
        "currency": "<currency isocode>",
        "name": "<new category name>"
    }
}

If a parent is defined::

{
    "status": 200,
    "response": {
        "id": <new category unique id>,
        "parent": <parent unique id>,
        "currency": "<currency isocode>",
        "name": "<new category name>"
    }
}

Read
====

Read a category

Request
-------

::

    GET /categories/<id>

* ``<id>``: unique id of the category

Response
--------

Example::

    {
        "status": 200,
        "response": {
            "children": [
                {
                    "children": [
                        {
                            "id": 14,
                            "currency": "EUR",
                            "name": "Electricity"
                        },
                        {
                            "id": 15,
                            "currency": "EUR",
                            "name": "Internet access"
                        }
                    ],
                    "id": 9,
                    "currency": "EUR",
                    "name": "Invoices"
                }
            ],
            "id": 2,
            "currency": "EUR",
            "name": "House"
        }
    }

Update
======

Update a category

Request
-------

::

    PUT /categories/<id>

* ``<id>``: unique id of the category

Data
----

All are optional

* ``name``: new name of the new category (max 50 chars)
* ``parent``: new parent of the category, or "NONE" to remove parent
* ``currency``: default currency for this category

Response
--------

Example::

    {
        "status": 200,
        "response": {
            "children": [
                {
                    "children": [
                        {
                            "id": 14,
                            "currency": "EUR",
                            "name": "Electricity"
                        },
                        {
                            "id": 15,
                            "currency": "EUR",
                            "name": "Internet access"
                        }
                    ],
                    "id": 9,
                    "currency": "EUR",
                    "name": "Invoices"
                }
            ],
            "id": 2,
            "currency": "EUR",
            "name": "House"
        }
    }

Delete
======

Delete a category.

Consequences on other stuff will be detailed later.

Request
-------

::

    DELETE /categories/<id>

* ``<id>``: unique id of the category

Response
--------

::

    {
        "status": 200,
        "response": "OK Deleted"
    }
