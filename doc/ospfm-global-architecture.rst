#########################
OSPFM global architecture
#########################

OSPFM is divided into multiple different subparts, implemented as Django
applications.

The following schema explains interaction between them::

                    +-----------------------+
                    | +-----------------------+
                    | | +-----------------------+
                    | | |                       |
                    +-| | back-end applications |
                      +-|                       |
                        +-----------------------+

                      /              |            \
                     /               |             \
                    /                |              \
                   /                 |               \
 +----------------------+ +--------------------+ +---------------------+
 |                      | |                    | |  subscription and   |
 | mobile web interface | | rich web interface | | billing application |
 |                      | |                    | |  (not Open Source)  |
 +----------------------+ +--------------------+ +---------------------+

Back-end applications
=====================

Data storage and manipulation is done in Django applications.

Rich web interface
==================

The rich web interface is oriented toward users on computers (and maybe on
tablets).

Mobile web interface
====================

The mobile web interface is optimized for smartphones (and maybe tablets).

Subscription and billing application
====================================

A subscription and billing application should manage users and their
authorizations. This part is not distributed as an Open Source product.
