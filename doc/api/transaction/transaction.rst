############################
OSPFM REST API : Transaction
############################

This document details the OSPFM REST API for Transaction requests.

List
====

List all user's transactions

Request
-------

::

    GET /transactions

Response
--------

::

    {
        "status": 200,
        "response": [
            {
                "currency": "<isocode>",
                "amount": <amount of the transaction>,
                "accounts": [
                    {
                        "currency": "<isocode>",
                        "amount": <amount for this account>,
                        "verified": <boolean>,
                        "id": <account id>,
                        "name": "<account name>"
                    },
    [...]
                ],
                "description": "<transaction description>",
                "date": "<transaction date>",
                "original_description": "<transaction original description>",
                "id": <transaction unique id>,
                "categories": [
                    {
                        "currency": "<isocode>",
                        "amount": <amount for the category>,
                        "id": <category id>,
                        "name": "<category name>"
                    },
    [...]
                ]
            },
            {
                "currency": "<isocode>",
                "amount": <amount of the transaction>,
                "accounts": [
                    {
                        "currency": "<isocode>",
                        "amount": <amount for this account>,
                        "verified": <boolean>,
                        "id": <account id>,
                        "name": "<account name>"
                    },
    [...]
                ],
                "description": "<transaction description>",
                "date": "<transaction date>",
                "original_description": "<transaction original description>",
                "id": <transaction unique id>,
                "categories": [
                    {
                        "currency": "<isocode>",
                        "amount": <amount for the category>,
                        "id": <category id>,
                        "name": "<category name>"
                    },
    [...]
                ]
            },
    [...]
        ]
    }

Create
======

Create a new transaction

For examples on how to add transactions, see
`the "adding a transaction" page <../adding_a_transaction.html>`_.

Request
-------

::

    POST /transactions

Data
----

* ``description``: description (name) of the transaction
* ``original_description``: original description of the transaction (optional)
* ``amount``: total amount of the transaction, in the currency specified
* ``currency``: currency of the transaction
* ``date``: date of the transaction
* ``accounts``: list of accounts for this transaction (see below)
* ``categories``: list of categories for this transaction (see below)

Accounts
''''''''

The ``accounts`` parameter is a JSON-formated string::

    [
        {
            "account": <account id>,
            "amount": <amount for this account, in the account currency>
        },
        {
            "account": <account id>,
            "amount": <amount for this account, in the account currency>
        },
    [...]
    ]

If the specified account does not exist or is not owned by the current user,
the association is silently ignored; making sure the account belongs to the
user is the frontend's job.

Categories
''''''''''

The ``categories`` parameter is a JSON-formated string::

    [
        {
            "category": <category id>,
            "amount": <amount for this category, in the category currency>
        }
    [...]
    ]

If the specified category does not exist or is not owned by the current user,
the association is silently ignored; making sure the category belongs to the
user is the frontend's job.

Response
--------

::

    {
        "status": 200,
        "response": {
            "currency": "<isocode>",
            "amount": <amount of the transaction>,
            "accounts": [
                {
                    "currency": "<isocode>",
                    "amount": <amount for this account>,
                    "verified": <boolean>,
                    "id": <account id>,
                    "name": "<account name>"
                },
    [...]
            ],
            "description": "<transaction description>",
            "date": "<transaction date>",
            "original_description": "<transaction original description>",
            "id": <transaction unique id>,
            "categories": [
                {
                    "currency": "<isocode>",
                    "amount": <amount for the category>,
                    "id": <category id>,
                    "name": "<category name>"
                },
    [...]
            ]
        }
    }

Read
====

Read a transaction

Request
-------

::

    GET /transactions/<id>

* ``<id>``: unique id of the transaction

Response
--------

::

    {
        "status": 200,
        "response": {
            "currency": "<isocode>",
            "amount": <amount of the transaction>,
            "accounts": [
                {
                    "currency": "<isocode>",
                    "amount": <amount for this account>,
                    "verified": <boolean>,
                    "id": <account id>,
                    "name": "<account name>"
                },
    [...]
            ],
            "description": "<transaction description>",
            "date": "<transaction date>",
            "original_description": "<transaction original description>",
            "id": <transaction unique id>,
            "categories": [
                {
                    "currency": "<isocode>",
                    "amount": <amount for the category>,
                    "id": <category id>,
                    "name": "<category name>"
                },
    [...]
            ]
        }
    }

Update
======

Update a transaction

Request
-------

::

    POST /transactions/<id>

* ``<id>``: unique id of the transaction

Data
----

All are optional.

* ``description``: description (name) of the transaction
* ``amount``: total amount of the transaction, in the currency specified
* ``currency``: currency of the transaction
* ``date``: date of the transaction
* ``accounts``: list of accounts for this transaction (see below)
* ``categories``: list of categories for this transaction (see below)

Accounts
''''''''

The ``accounts`` parameter is a JSON-formated string::

    [
        {
            "account": <account id>,
            "amount": <amount for this account, in the account currency>
        },
        {
            "account": <account id>,
            "amount": <amount for this account, in the account currency>
        },
    [...]
    ]

If the specified account does not exist or is not owned by the current user,
the association is silently ignored; making sure the account belongs to the
user is the frontend's job.

If the specified account is already linked, only its amount is changed (if it
is necessary).

If an already-linked account is not specified, the link is deleted.

If the "accounts" parameter is not given, no action is done on links to
accounts.

Categories
''''''''''

The ``categories`` parameter is a JSON-formated string::

    [
        {
            "category": <category id>,
            "amount": <amount for this category, in the category currency>
        }
    [...]
    ]

If the specified category does not exist or is not owned by the current user,
the association is silently ignored; making sure the category belongs to the
user is the frontend's job.

If the specified category is already linked, only its amount is changed (if it
is necessary).

If an already-linked category is not specified, the link is deleted.

If the "categories" parameter is not given, no action is done on links to
categories.

Response
--------

::

    {
        "status": 200,
        "response": {
            "currency": "<isocode>",
            "amount": <amount of the transaction>,
            "accounts": [
                {
                    "currency": "<isocode>",
                    "amount": <amount for this account>,
                    "verified": <boolean>,
                    "id": <account id>,
                    "name": "<account name>"
                },
    [...]
            ],
            "description": "<transaction description>",
            "date": "<transaction date>",
            "original_description": "<transaction original description>",
            "id": <transaction unique id>,
            "categories": [
                {
                    "currency": "<isocode>",
                    "amount": <amount for the category>,
                    "id": <category id>,
                    "name": "<category name>"
                },
    [...]
            ]
        }
    }

Delete
======

Delete a transaction

Request
-------

::

    DELETE /transactions/<id>

* ``<id>``: unique id of the transaction

Response
--------

::

    {
        "status": 200,
        "response": "OK Deleted"
    }
