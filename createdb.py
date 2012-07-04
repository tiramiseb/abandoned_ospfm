#!/usr/bin/env python

#    Copyright 2012 Sebastien Maccagnoni-Munch
#
#    This file is part of OSPFM.
#
#    OSPFM is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OSPFM is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with OSPFM.  If not, see <http://www.gnu.org/licenses/>.

import sys

from ospfm import database as db
from ospfm.core import models as core

def populate_test_db():
    # Currencies
    euro = core.Currency(symbol='EUR', name='Euro')
    dollar = core.Currency(symbol='USD', name='US Dollar')
    yen = core.Currency(symbol='JPY', name='Yen')
    db.session.add_all((euro, dollar, yen))

    # Users
    alice = core.User(username='alice', first_name='Alice',
                      last_name='In Wonderland', preferred_currency=euro)
    bob = core.User(username='bob', first_name='Bob', last_name='Sponge',
                    preferred_currency=dollar)
    carol = core.User(username='carol', first_name='Carol', last_name='Markus',
                      preferred_currency=yen)
    db.session.add_all((alice, bob, carol))

    # Users email addresses
    alice1 = core.UserEmail(user=alice, email_address='alice@wonderland.org')
    alice2 = core.UserEmail(user=alice, email_address='alice@springs.au')
    bob1 = core.UserEmail(user=bob, email_address='spongebob@gmail.com')
    carol1 = core.UserEmail(user=carol, email_address='carol@markus.space')
    carol2 = core.UserEmail(user=carol, email_address='carol.markus@gmail.com')
    db.session.add_all((alice1, alice2, bob1, carol1, carol2))

    # Users contacts
    alice_bob = core.UserContact(user=alice, contact=bob)
    alice_carol = core.UserContact(user=alice, contact=carol)
    bob_carol = core.UserContact(user=bob, contact=carol)
    carol_alice = core.UserContact(user=carol, contact=alice)
    db.session.add_all((alice_bob, alice_carol, bob_carol, carol_alice))

    db.session.commit()

if __name__ == '__main__':
    db.init_db()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'testdb':
            populate_test_db()
