#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from ospfm.transaction import models as transaction

def populate_test_db():
    euro = core.Currency.query.filter(core.Currency.symbol=='EUR').one()
    dollar = core.Currency.query.filter(core.Currency.symbol=='USD').one()
    yen = core.Currency.query.filter(core.Currency.symbol=='JPY').one()

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
    bob_carol = core.UserContact(user=bob, contact=carol)
    carol_alice = core.UserContact(user=carol, contact=alice)
    db.session.add_all((alice_bob, bob_carol, carol_alice))

    # Accounts
    acct1 = transaction.Account(name='Default account', currency=euro,
                                start_balance=0)
    acct2 = transaction.Account(name='Shared account', currency=euro,
                                start_balance=100)
    acct3 = transaction.Account(name='Default account', currency=euro,
                                start_balance=12.34)
    alice_acct1 = transaction.AccountOwner(account=acct1, owner=alice)
    alice_acct2 = transaction.AccountOwner(account=acct2, owner=alice)
    bob_acct2 = transaction.AccountOwner(account=acct2, owner=bob)
    carol_acct3 = transaction.AccountOwner(account=acct3, owner=carol)
    db.session.add_all((acct1, acct2, acct3,
                        alice_acct1, alice_acct2, bob_acct2, carol_acct3))

    # Categories
    alicecat1 = transaction.Category(owner=alice, name='Car', currency=euro)
    alicecat2 = transaction.Category(owner=alice, name='House', currency=euro)
    alicecat3 = transaction.Category(owner=alice, name='Fun', currency=euro)
    alicecat4 = transaction.Category(owner=alice, parent=alicecat1,
                                     name='Insurance', currency=euro)
    alicecat5 = transaction.Category(owner=alice, parent=alicecat1,
                                     name='Fuel', currency=euro)
    alicecat6 = transaction.Category(owner=alice, parent=alicecat2,
                                     name='Invoices', currency=euro)
    alicecat7 = transaction.Category(owner=alice, parent=alicecat6,
                                     name='Electricity', currency=euro)
    alicecat8 = transaction.Category(owner=alice, parent=alicecat6,
                                     name='Internet access', currency=euro)
    alicecat9 = transaction.Category(owner=alice, parent=alicecat3,
                                     name='Danceclub', currency=euro)
    bobcat1 = transaction.Category(owner=bob, name='Car', currency=euro)
    bobcat2 = transaction.Category(owner=bob, name='Fun', currency=dollar)
    bobcat3 = transaction.Category(owner=bob, parent=bobcat1,
                                   name='Fuel', currency=euro)
    bobcat4 = transaction.Category(owner=bob, parent=bobcat2,
                                   name='Books', currency=dollar)
    bobcat5 = transaction.Category(owner=bob, parent=bobcat2,
                                   name='Music', currency=dollar)
    carolcat1 = transaction.Category(owner=carol, name='House', currency=yen)

    db.session.add_all((
        alicecat1, alicecat2, alicecat3, alicecat4, alicecat5, alicecat6,
        alicecat7, alicecat8, alicecat9, bobcat1, bobcat2, bobcat3, bobcat4,
        bobcat5, carolcat1
    ))

    db.session.commit()

def populate_currencies():
    # The following currencies are not created because they are not taken into
    # account by OSPFM's exchange rates source, open source Exchange Rates:
    # http://openexchangerates.org/
    #
    # BOV (Bolivian Mvdol)
    # COU (Colombian Unidad de Valor Real)
    # CUC (Cuban convertible peso)
    # ERN (Eritrean nakfa)
    # KYD (Cayman Islands dollar)
    # MXV (Mexican Unidad de Inversion)
    # SSP (South Sudanese pound)
    # XAG (Silver (ounce))
    # XAU (Gold (ounce))
    # XPD (Palladieu (ounce))
    # XPT (Platinium (ounce))
    #
    # Sorry to those who would have wanted to use these currencies.
    # Users may still define them and manage their rates as user-defined currencies
    db.session.add_all((
        core.Currency(symbol='AED', name=u'United Arab Emirates dirham'),
        core.Currency(symbol='AFN', name=u'Afghan afghani'),
        core.Currency(symbol='ALL', name=u'Albanian lek'),
        core.Currency(symbol='AMD', name=u'Armenian dram'),
        core.Currency(symbol='ANG', name=u'Netherlands Antillean guilder'),
        core.Currency(symbol='AOA', name=u'Angolan kwanza'),
        core.Currency(symbol='ARS', name=u'Argentine peso'),
        core.Currency(symbol='AUD', name=u'Australian dollar'),
        core.Currency(symbol='AWG', name=u'Aruban florin'),
        core.Currency(symbol='AZN', name=u'Azerbaijani manat'),
        core.Currency(symbol='BAM', name=u'Bosnia and Herzegovina convertible mark'),
        core.Currency(symbol='BBD', name=u'Barbados dollar'),
        core.Currency(symbol='BDT', name=u'Bangladeshi taka'),
        core.Currency(symbol='BGN', name=u'Bulgarian lev'),
        core.Currency(symbol='BHD', name=u'Bahraini dinar'),
        core.Currency(symbol='BIF', name=u'Burundian franc'),
        core.Currency(symbol='BMD', name=u'Bermudian dollar'),
        core.Currency(symbol='BND', name=u'Brunei dollar'),
        core.Currency(symbol='BOB', name=u'Boliviano'),
        core.Currency(symbol='BRL', name=u'Brazilian real'),
        core.Currency(symbol='BSD', name=u'Bahamian dollar'),
        core.Currency(symbol='BTN', name=u'Bhutanese ngultrum'),
        core.Currency(symbol='BWP', name=u'Botswana pula'),
        core.Currency(symbol='BYR', name=u'Belarusian ruble'),
        core.Currency(symbol='BZD', name=u'Belize dollar'),
        core.Currency(symbol='CAD', name=u'Canadian dollar'),
        core.Currency(symbol='CDF', name=u'Congolese franc'),
        core.Currency(symbol='CHF', name=u'Swiss franc'),
        core.Currency(symbol='CLF', name=u'Unidad de Fomento'),
        core.Currency(symbol='CLP', name=u'Chilean peso'),
        core.Currency(symbol='CNY', name=u'Chinese yuan'),
        core.Currency(symbol='COP', name=u'Colombian peso'),
        core.Currency(symbol='CRC', name=u'Costa Rican colon'),
        core.Currency(symbol='CUP', name=u'Cuban peso'),
        core.Currency(symbol='CVE', name=u'Cape Verde escudo'),
        core.Currency(symbol='CZK', name=u'Czech koruna'),
        core.Currency(symbol='DJF', name=u'Djiboutian franc'),
        core.Currency(symbol='DKK', name=u'Danish krone'),
        core.Currency(symbol='DOP', name=u'Dominican peso'),
        core.Currency(symbol='DZD', name=u'Algerian dinar'),
        core.Currency(symbol='EGP', name=u'Egyptian pound'),
        core.Currency(symbol='ETB', name=u'Ethiopian birr'),
        core.Currency(symbol='EUR', name=u'Euro'),
        core.Currency(symbol='FJD', name=u'Fiji dollar'),
        core.Currency(symbol='FKP', name=u'Falkland Islands pound'),
        core.Currency(symbol='GBP', name=u'Pound sterling'),
        core.Currency(symbol='GEL', name=u'Georgian lari'),
        core.Currency(symbol='GHS', name=u'Ghanaian cedi'),
        core.Currency(symbol='GIP', name=u'Gibraltar pound'),
        core.Currency(symbol='GMD', name=u'Gambian dalasi'),
        core.Currency(symbol='GNF', name=u'Guinean franc'),
        core.Currency(symbol='GTQ', name=u'Guatemalan quetzal'),
        core.Currency(symbol='GYD', name=u'Guyanese dollar'),
        core.Currency(symbol='HKD', name=u'Hong Kong dollar'),
        core.Currency(symbol='HNL', name=u'Honduran lempira'),
        core.Currency(symbol='HRK', name=u'Croatian kuna'),
        core.Currency(symbol='HTG', name=u'Haitian gourde'),
        core.Currency(symbol='HUF', name=u'Hungarian forint'),
        core.Currency(symbol='IDR', name=u'Indonesian rupiah'),
        core.Currency(symbol='ILS', name=u'Israeli new sheqel'),
        core.Currency(symbol='INR', name=u'Indian rupee'),
        core.Currency(symbol='IQD', name=u'Iraqi dinar'),
        core.Currency(symbol='IRR', name=u'Iranian rial'),
        core.Currency(symbol='ISK', name=u'Icelandic króna'),
        core.Currency(symbol='JMD', name=u'Jamaican dollar'),
        core.Currency(symbol='JOD', name=u'Jordanian dinar'),
        core.Currency(symbol='JPY', name=u'Japanese yen'),
        core.Currency(symbol='KES', name=u'Kenyan shilling'),
        core.Currency(symbol='KGS', name=u'Kyrgyzstani som'),
        core.Currency(symbol='KHR', name=u'Cambodian riel'),
        core.Currency(symbol='KMF', name=u'Comoro franc'),
        core.Currency(symbol='KPW', name=u'North Korean won'),
        core.Currency(symbol='KRW', name=u'South Korean won'),
        core.Currency(symbol='KWD', name=u'Kuwaiti dinar'),
        core.Currency(symbol='KZT', name=u'Kazakhstani tenge'),
        core.Currency(symbol='LAK', name=u'Lao kip'),
        core.Currency(symbol='LBP', name=u'Lebanese pound'),
        core.Currency(symbol='LKR', name=u'Sri Lankan rupee'),
        core.Currency(symbol='LRD', name=u'Liberian dollar'),
        core.Currency(symbol='LSL', name=u'Lesotho loti'),
        core.Currency(symbol='LTL', name=u'Lithuanian litas'),
        core.Currency(symbol='LVL', name=u'Latvian lats'),
        core.Currency(symbol='LYD', name=u'Libyan dinar'),
        core.Currency(symbol='MAD', name=u'Moroccan dirham'),
        core.Currency(symbol='MDL', name=u'Moldovan leu'),
        core.Currency(symbol='MGA', name=u'Malagasy ariary'),
        core.Currency(symbol='MKD', name=u'Macedonian denar'),
        core.Currency(symbol='MMK', name=u'Myanma kyat'),
        core.Currency(symbol='MNT', name=u'Mongolian tugrik'),
        core.Currency(symbol='MOP', name=u'Macanese pataca'),
        core.Currency(symbol='MRO', name=u'Mauritanian ouguiya'),
        core.Currency(symbol='MUR', name=u'Mauritian rupee'),
        core.Currency(symbol='MVR', name=u'Maldivian rufiyaa'),
        core.Currency(symbol='MWK', name=u'Malawian kwacha'),
        core.Currency(symbol='MXN', name=u'Mexican peso'),
        core.Currency(symbol='MYR', name=u'Malaysian ringgit'),
        core.Currency(symbol='MZN', name=u'Mozambican metical'),
        core.Currency(symbol='NAD', name=u'Namibian dollar'),
        core.Currency(symbol='NGN', name=u'Nigerian naira'),
        core.Currency(symbol='NIO', name=u'Nicaraguan córdoba'),
        core.Currency(symbol='NOK', name=u'Norwegian krone'),
        core.Currency(symbol='NPR', name=u'Nepalese rupee'),
        core.Currency(symbol='NZD', name=u'New Zealand dollar'),
        core.Currency(symbol='OMR', name=u'Omani rial'),
        core.Currency(symbol='PAB', name=u'Panamanian balboa'),
        core.Currency(symbol='PEN', name=u'Peruvian nuevo sol'),
        core.Currency(symbol='PGK', name=u'Papua New Guinean kina'),
        core.Currency(symbol='PHP', name=u'Philippine peso'),
        core.Currency(symbol='PKR', name=u'Pakistani rupee'),
        core.Currency(symbol='PLN', name=u'Polish złoty'),
        core.Currency(symbol='PYG', name=u'Paraguayan guaraní'),
        core.Currency(symbol='QAR', name=u'Qatari riyal'),
        core.Currency(symbol='RON', name=u'Romanian new leu'),
        core.Currency(symbol='RSD', name=u'Serbian dinar'),
        core.Currency(symbol='RUB', name=u'Russian rouble'),
        core.Currency(symbol='RWF', name=u'Rwandan franc'),
        core.Currency(symbol='SAR', name=u'Saudi riyal'),
        core.Currency(symbol='SBD', name=u'Solomon Islands dollar'),
        core.Currency(symbol='SCR', name=u'Seychelles rupee'),
        core.Currency(symbol='SDG', name=u'Sudanese pound'),
        core.Currency(symbol='SEK', name=u'Swedish krona'),
        core.Currency(symbol='SGD', name=u'Singapore dollar'),
        core.Currency(symbol='SHP', name=u'Saint Helena pound'),
        core.Currency(symbol='SLL', name=u'Sierra Leonean leone'),
        core.Currency(symbol='SOS', name=u'Somali shilling'),
        core.Currency(symbol='SRD', name=u'Surinamese dollar'),
        core.Currency(symbol='STD', name=u'São Tomé and Príncipe dobra'),
        core.Currency(symbol='SYP', name=u'Syrian pound'),
        core.Currency(symbol='SZL', name=u'Swazi lilangeni'),
        core.Currency(symbol='THB', name=u'Thai baht'),
        core.Currency(symbol='TJS', name=u'Tajikistani somoni'),
        core.Currency(symbol='TMT', name=u'Turkmenistani manat'),
        core.Currency(symbol='TND', name=u'Tunisian dinar'),
        core.Currency(symbol='TOP', name=u'Tongan paʻanga'),
        core.Currency(symbol='TRY', name=u'Turkish lira'),
        core.Currency(symbol='TTD', name=u'Trinidad and Tobago dollar'),
        core.Currency(symbol='TWD', name=u'New Taiwan dollar'),
        core.Currency(symbol='TZS', name=u'Tanzanian shilling'),
        core.Currency(symbol='UAH', name=u'Ukrainian hryvnia'),
        core.Currency(symbol='UGX', name=u'Ugandan shilling'),
        core.Currency(symbol='USD', name=u'United States dollar'),
        core.Currency(symbol='UYI', name=u'Uruguay Peso en Unidades Indexadas'),
        core.Currency(symbol='UYU', name=u'Uruguayan peso'),
        core.Currency(symbol='UZS', name=u'Uzbekistan som'),
        core.Currency(symbol='VEF', name=u'Venezuelan bolívar fuerte'),
        core.Currency(symbol='VND', name=u'Vietnamese đồng'),
        core.Currency(symbol='VUV', name=u'Vanuatu vatu'),
        core.Currency(symbol='WST', name=u'Samoan tala'),
        core.Currency(symbol='XAF', name=u'CFA franc BEAC'),
        core.Currency(symbol='XCD', name=u'East Caribbean dollar'),
        core.Currency(symbol='XOF', name=u'CFA Franc BCEAO'),
        core.Currency(symbol='XPF', name=u'CFP franc'),
        core.Currency(symbol='YER', name=u'Yemeni rial'),
        core.Currency(symbol='ZAR', name=u'South African rand'),
        core.Currency(symbol='ZMK', name=u'Zambian kwacha'),
        core.Currency(symbol='ZWL', name=u'Zimbabwe dollar')
    ))
    db.session.commit()

if __name__ == '__main__':
    db.init_db()

    populate_currencies()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'testdb':
            populate_test_db()
