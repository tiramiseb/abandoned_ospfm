############################################
OSPFM REST API : transaction additional data
############################################

This document details automatic additional data for the "transaction" subpart.

accountbalance
==============

An account balance has been modified.

Format::

    {
        "id": <account id>,
        "balance": <balance>
    }

totalbalance
============

The total balance has been modified (either the sum or the currency).

Format::

    {
        "balance": <balance>,
        "currency": "<currency isocode>"
    }
