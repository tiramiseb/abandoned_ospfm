##############
OSPFM REST API
##############

This documentation details the OSPFM REST API...

Response format
===============

All responses have the following format::

    {
        "status": <status code>,
        "response": <response>,
        "additional": <additional data>
    }

* The status code is the same as the HTTP error code (see details below)
* The response is different for each request type: this part is detailed in
  the following pages
* The additional data is optional: when the server needs to send data to the
  client, it is placed in a json dictonary here; details in the following pages

Status codes
------------

* 200: No error
* 400: Bad request (generally, wrong data in the request)
* 401: Unauthorized (the user needs to identify himself)
* 403: Forbidden (generally, trying to access an object belonging to another
  user)
* 404: Not found (trying to access an object that doesn't exist)

Additional data example
-----------------------

::

    {
        "accountbalance": {
            "id": 5,
            "balance": 45.80
        },
        "totalbalance": {
            "balance": 1420.47,
            "currency": "USD"
        }
    }

Core stuff
==========

* `Currency <core/currency.html>`_
* `User <core/user.html>`_

Transaction stuff
=================

* `Account <transaction/account.html>`_
* `Category <transaction/category.html>`_
* `Transaction <transaction/transaction.html>`_
* `additional data <transaction/additional.html>`_
