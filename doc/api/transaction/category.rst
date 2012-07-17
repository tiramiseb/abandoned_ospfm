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
                    "name": "Fuel"
                },
                {
                    "id": 7,
                    "name": "Insurance"
                }
            ],
            "id": 1,
            "name": "Car"
        },
        {
            "children": [
                {
                    "id": 10,
                    "name": "Danceclub"
                }
            ],
            "id": 3,
            "name": "Fun"
        },
        {
            "children": [
                {
                    "children": [
                        {
                            "id": 14,
                            "name": "Electricity"
                        },
                        {
                            "id": 15,
                            "name": "Internet access"
                        }
                    ],
                    "id": 9,
                    "name": "Invoices"
                }
            ],
            "id": 2,
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

Response
--------

If no parent is defined::

{
    "status": 200,
    "response": {
        "id": <new category unique id>,
        "name": "<new category name>"
    }
}

If a parent is defined::

{
    "status": 200,
    "response": {
        "id": <new category unique id>,
        "parent": <parent unique id>,
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
                            "name": "Electricity"
                        },
                        {
                            "id": 15,
                            "name": "Internet access"
                        }
                    ],
                    "id": 9,
                    "name": "Invoices"
                }
            ],
            "id": 2,
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
                            "name": "Electricity"
                        },
                        {
                            "id": 15,
                            "name": "Internet access"
                        }
                    ],
                    "id": 9,
                    "name": "Invoices"
                }
            ],
            "id": 2,
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
