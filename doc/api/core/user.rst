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
        "username": "<username>",
        "first_name": "<first name>",
        "last_name": "<last name>",
    }

For the user's own information::

    {
        "username": "<username>",
        "first_name": "<first name>",
        "last_name": "<last name>",
        "preferred_currency": "<currency isocode>",
        "emails": [
            {
                "notification": <true or false>,
                "confirmed": <true or false>,
                "address": "<email address>",
            },
            [...]
        ]
    }

Update
======

Update a user's details.

A user can only update his own data.

Request
-------

::

    POST /users/<username>

* ``<username>``: username of the user to update

::

    POST /users/me

Data
----

* ``first_name``: user's first name
* ``last_name``: user's last name
* ``preferred_currency``: user's preferred currency
* ``emails`` : modifications to email addresses (see below)

Modifications to email addresses
''''''''''''''''''''''''''''''''

The ``emails`` parameter is a JSON-formatted string::

    {
        "add":[
            "<email address>",
    [...]
        ],
        "remove":[
            "<email address>",
    [...]
        ],
        "enablenotifications":[
            "<email address>",
        ],
        "disablenotifications":[
            "<email address>",
        ]
    }

Response
--------

::

    {
        "username": "<username>",
        "first_name": "<first name>",
        "last_name": "<last name>",
        "preferred_currency": "<currency isocode>",
        "emails": [
            {
                "notification": <true or false>,
                "confirmed": <true or false>,
                "address": "<email address>",
            },
            [...]
        ]
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

    [
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

List contacts
=============

List all current user's contacts

Request
-------

::

    GET /contacts

Response
--------

::

    [
        {
            "username": "<username>",
            "first_name": "<first name>",
            "last_name": "<last name>",
            "comment": "<personal comment>"
        },
        {
            "username": "<username>",
            "first_name": "<first name>",
            "last_name": "<last name>",
            "comment": "<personal comment>"
        }
        [...]
    ]

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
* ``comment``: personal comment on this contact

Response
--------

::

    {
        "username": "<username>",
        "first_name": "<first name>",
        "last_name": "<last name>",
        "comment": "<personal comment"
    }

Read a contact
==============

Read a contact for the current user

Request
-------

::

    GET /contacts/<username>

* ``<username>``: username of the contact

Response
--------

::

    {
        "username": "<username>",
        "first_name": "<first name>",
        "last_name": "<last name>",
        "comment": "<personal comment"
    }

Update a contact
================

Update a contact for the current user

Request
-------

::

    POST /contacts/<username>

* ``<username>``: username of the contact

Data
----

* ``comment``: personal comment on this contact

Response
--------

::

    {
        "username": "<username>",
        "first_name": "<first name>",
        "last_name": "<last name>",
        "comment": "<personal comment"
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

    "OK Deleted"

Preferences
===========

List all current user's preferences

Request
-------

::

    GET /preferences

Response
--------

::

    [
        {
            "name": "<preference name>",
            "value": "<preference value>"
        },
        {
            "name": "<preference name>",
            "value": "<preference value>"
        }
        [...]
    ]

Read a preference
=================

Read a preference for the current user

Request
-------

::

    GET /preference/<preference name>

* ``<preference name>``: name of the preference

Response
--------

::

    {
        "name": "<preference name>",
        "value": "<preference value>"
    }


Create or update a preference
=============================

Create or update a preference for the current user

Request
-------

::

    POST /preferences/<preference name>


* ``<preference name>``: name of the preference

Data
----

* ``value``: value to set for the preference

Response
--------

::

    {
        "name": "<preference name>",
        "value": "<preference value>"
    }

Delete a preference
===================

Delete a preference from the current user

Request
-------

::

    DELETE /preferences/<preference name>

* ``<preference name>``: name of the preference

Response
--------

::

    "OK Deleted"
