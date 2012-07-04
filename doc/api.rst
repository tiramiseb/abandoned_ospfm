==============
OSPFM REST API
==============

This document details the OSPFM REST API.

Core
####

Currency
========

A user can only see his own currencies and globally-defined currencies.
A user can only create, update or delete his own user-defined currencies.

====================================== ================== ================================================
Request                                Data               Action
====================================== ================== ================================================
GET /currencies                                           List all currencies
POST /currencies                       symbol, name, rate Create a new user-defined currency
GET /currencies/<symbol>                                  Read a single currency
PUT /currencies/<symbol>               symbol, name, rate Update a user-defined currency
DELETE /currencies/<symbol>                               Delete a user-defined currency
GET /currencies/<symbol>/rate/<symbol>                    Get the exchange rate from a currency to another
====================================== ================== ================================================

User
====

======================================= ========================================= ===========================================================
Request                                 Data                                      Action
======================================= ========================================= ===========================================================
GET /users/<username>                                                             Read a single user (with more details for the current user)
PUT /users/<username>                   first_name, last_name, preferred_currency Update an user (works only for the current user)
GET /users/search/<string>                                                        Search for users whose names contain the string
GET /users/search/<string_containing_@>                                           Search for users having the specified email address
======================================= ========================================= ===========================================================

UserContact
===========

=========================== ======== =====================================
Request                     Data     Action
=========================== ======== =====================================
GET /contacts                        List all current user's contacts
POST /contacts              username Create a new contact for current user
DELETE /contacts/<username>          Delete a contact from current user
=========================== ======== =====================================

UserEmail
=========

============================== ============= ===========================================
Request                        Data          Action
============================== ============= ===========================================
GET /emails                                  List all current user's email addresses
POST /emails                   email_address Create a new email address for current user
PUT /emails/<email_address>    email_address Update a current user's email address
DELETE /emails/<email_address>               Delete a current user's email address
============================== ============= ===========================================
