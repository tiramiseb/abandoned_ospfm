#####################
OSPFM REST API : User
#####################

This document details the OSPFM REST API for User requests.

Read
====

Read a user's details.

More details are given when reading own data.

Request
-------

::

    GET /users/<username>

* ``<username>``: username of the user to read

::

    GET /users/me

Response
--------

For other users::

    {
        "status": 200,
        "response": {
            "username": "<username>",
            "first_name": "<first name>",
            "last_name": "<last name>",
        }
    }

For the user's own information::

    {
        "status": 200,
        "response": {
            "username": "<username>",
            "first_name": "<first name>",
            "last_name": "<last name>",
            "contacts": [
                {
                    "username": "<contact username>",
                    "first_name": "<contact first name>",
                    "last_name": "<contact last name>"
                },
    [...]
            ],
            "preferred_currency": "<currency symbol>",
            "emails": [
                "<email address>",
    [...]
            ]
        }
    }

Update
======

Update a user's details.

A user can only update his own data.

Request
-------

::

    PUT /users/<username>

* ``<username>``: username of the user to update

::

    PUT /users/me

Data
----

* ``first_name``: user's first name
* ``last_name``: user's last name
* ``preferred_currency``: user's preferred currency
* ``emails`` : modifications to email addresses (see below)

Modifications to email addresses
''''''''''''''''''''''''''''''''

The ``emails`` parameter is a string composed of email addresses prefixed with
"+" (to add an address) or "-" (to remove an address), separated by "&".

For example, to add "bob@example.com" and remove "bob@test.com"::

    +bob@example.com&-bob@test.com

Response
--------

::

    {
        "status": 200,
        "response": {
            "username": "<username>",
            "first_name": "<first name>",
            "last_name": "<last name>",
            "contacts": [
                {
                    "username": "<contact username>",
                    "first_name": "<contact first name>",
                    "last_name": "<contact last name>"
                },
    [...]
            ],
            "preferred_currency": "<currency symbol>",
            "emails": [
                "<email address>",
    [...]
            ]
        }
    }

Search
======

Search for users...

Request
-------

::

    GET /users/search/<string>

* ``<string>``: search for users whose name contain the string

::

    GET /users/search/<string_containing_@>

* ``<string_containing_@>``: search for users whose email address is exactly this

Response
--------

::

    {
        "status": 200,
        "response": [
            {
                "username": "<username>",
                "first_name": "<first name>",
                "last_name": "<last name>"
            },
            {
                "username": "<username>",
                "first_name": "<first name>",
                "last_name": "<last name>"
            }
    [...]
        ]
    }

Contacts
========

List all current user's contacts

Request
-------

::

    GET /contacts

Response
--------

::

    {
        "status": 200,
        "response": [
            {
                "username": "<username>",
                "first_name": "<first name>",
                "last_name": "<last name>"
            },
            {
                "username": "<username>",
                "first_name": "<first name>",
                "last_name": "<last name>"
            }
    [...]
        ]
    }

Create a contact
================

Create a new contact for the current user

Request
-------

::

    POST /contacts

Data
----

* ``username``: username of the contact

Response
--------

::

    {
        "status": 200,
        "response": {
            "username": "<username>",
            "first_name": "<first name>",
            "last_name": "<last name>",
        }
    }

Delete a contact
================

Delete a contact from the current user

Request
-------

::

    DELETE /contacts/<username>

* ``<username>``: username of the contact

Response
--------

::

    {
        "status": 200,
        "response": "OK Deleted"
    }
