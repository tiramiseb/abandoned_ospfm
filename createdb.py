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

import datetime, sys

from ospfm import database as db
from ospfm.core import models as core
from ospfm.transaction import models as transaction

def populate_test_db():
    euro = core.Currency.query.filter(core.Currency.isocode=='EUR').one()
    dollar = core.Currency.query.filter(core.Currency.isocode=='USD').one()
    yen = core.Currency.query.filter(core.Currency.isocode=='JPY').one()

    # Users
    alice = core.User(username='alice', first_name='Alice',
                      last_name='In Wonderland', preferred_currency=euro)
    bob = core.User(username='bob', first_name='Bob', last_name='Sponge',
                    preferred_currency=dollar)
    carol = core.User(username='carol', first_name='Carol', last_name='Markus',
                      preferred_currency=yen)
    db.session.add_all((alice, bob, carol))

    # Users email addresses
    somehash = '1234567890123456'
    alice1 = core.UserEmail(user=alice, email_address='alice@wonderland.org',
                            confirmation='OK')
    alice2 = core.UserEmail(user=alice, email_address='alice@springs.au',
                            confirmation=somehash)
    bob1 = core.UserEmail(user=bob, email_address='spongebob@gmail.com',
                          confirmation=somehash)
    carol1 = core.UserEmail(user=carol, email_address='carol@markus.space',
                            confirmation=somehash)
    carol2 = core.UserEmail(user=carol, email_address='carol.markus@gmail.com',
                            confirmation=somehash)
    db.session.add_all((alice1, alice2, bob1, carol1, carol2))

    # Users contacts
    alice_bob = core.UserContact(user=alice, contact=bob, comment="My brother")
    bob_carol = core.UserContact(user=bob, contact=carol)
    carol_alice = core.UserContact(user=carol, contact=alice)
    db.session.add_all((alice_bob, bob_carol, carol_alice))

    # Accounts
    acct1 = transaction.Account(name='Default account', currency=euro,
                                start_balance=0)
    acct2 = transaction.Account(name='Shared account', currency=dollar,
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

    # Transactions
    t1 = transaction.Transaction(owner=alice, description='Elec. bill',
                                 original_description='ELECTRIC COMPANY',
                                 amount=-83.42, currency=euro,
                                 date=datetime.date(2012, 2, 5))
    ta1 = transaction.TransactionAccount(transaction=t1, account=acct1,
                                         amount=-83.42)
    tc1 = transaction.TransactionCategory(transaction=t1, category=alicecat7,
                                          amount=-83.42)
    t2 = transaction.Transaction(owner=alice, description='Transfer',
                                 original_description='Transfer',
                                 amount=0, currency=dollar,
                                 date=datetime.date(2012, 2, 7))
    ta2_1 = transaction.TransactionAccount(transaction=t2, account=acct2,
                                           amount=-200)
    ta2_2 = transaction.TransactionAccount(transaction=t2, account=acct1,
                                           amount=158.31)
    db.session.add_all((t1, ta1, tc1, t2, ta2_1, ta2_2))

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
    # XPD (Palladium (ounce))
    # XPT (Platinium (ounce))
    #
    # Sorry to those who would have wanted to use these currencies.
    # Users may still define them and manage their rates as user-defined currencies
    db.session.add_all((
        core.Currency(isocode='AED', name=u'United Arab Emirates dirham', symbol=u'DH'),
        core.Currency(isocode='AFN', name=u'Afghan afghani', symbol=u'AFN'),
        core.Currency(isocode='ALL', name=u'Albanian lek', symbol=u'L'),
        core.Currency(isocode='AMD', name=u'Armenian dram', symbol=u'AMD'),
        core.Currency(isocode='ANG', name=u'Netherlands Antillean guilder', symbol=u'ƒ'),
        core.Currency(isocode='AOA', name=u'Angolan kwanza', symbol=u'Kz'),
        core.Currency(isocode='ARS', name=u'Argentine peso', symbol=u'$'),
        core.Currency(isocode='AUD', name=u'Australian dollar', symbol=u'AU$'),
        core.Currency(isocode='AWG', name=u'Aruban florin', symbol=u'ƒ'),
        core.Currency(isocode='AZN', name=u'Azerbaijani manat', symbol=u'm'),
        core.Currency(isocode='BAM', name=u'Bosnia and Herzegovina convertible mark', symbol=u'KM'),
        core.Currency(isocode='BBD', name=u'Barbados dollar', symbol=u'$'),
        core.Currency(isocode='BDT', name=u'Bangladeshi taka', symbol=u'৳'),
        core.Currency(isocode='BGN', name=u'Bulgarian lev', symbol=u'лв'),
        core.Currency(isocode='BHD', name=u'Bahraini dinar', symbol=u'BD'),
        core.Currency(isocode='BIF', name=u'Burundian franc', symbol=u'FBu'),
        core.Currency(isocode='BMD', name=u'Bermudian dollar', symbol=u'$'),
        core.Currency(isocode='BND', name=u'Brunei dollar', symbol=u'$'),
        core.Currency(isocode='BOB', name=u'Boliviano', symbol=u'Bs'),
        core.Currency(isocode='BRL', name=u'Brazilian real', symbol=u'R$'),
        core.Currency(isocode='BSD', name=u'Bahamian dollar', symbol=u'$'),
        core.Currency(isocode='BTN', name=u'Bhutanese ngultrum', symbol=u'Nu'),
        core.Currency(isocode='BWP', name=u'Botswana pula', symbol=u'P'),
        core.Currency(isocode='BYR', name=u'Belarusian ruble', symbol=u'Br'),
        core.Currency(isocode='BZD', name=u'Belize dollar', symbol=u'$'),
        core.Currency(isocode='CAD', name=u'Canadian dollar', symbol=u'$'),
        core.Currency(isocode='CDF', name=u'Congolese franc', symbol=u'FC'),
        core.Currency(isocode='CHF', name=u'Swiss franc', symbol=u'Fr'),
        core.Currency(isocode='CLF', name=u'Unidad de Fomento', symbol=u'UF'),
        core.Currency(isocode='CLP', name=u'Chilean peso', symbol=u'$'),
        core.Currency(isocode='CNY', name=u'Chinese yuan', symbol=u'元'),
        core.Currency(isocode='COP', name=u'Colombian peso', symbol=u'$'),
        core.Currency(isocode='CRC', name=u'Costa Rican colon', symbol=u'₡'),
        core.Currency(isocode='CUP', name=u'Cuban peso', symbol=u'$'),
        core.Currency(isocode='CVE', name=u'Cape Verde escudo', symbol=u'$'),
        core.Currency(isocode='CZK', name=u'Czech koruna', symbol=u'Kč'),
        core.Currency(isocode='DJF', name=u'Djiboutian franc', symbol=u'Fdj'),
        core.Currency(isocode='DKK', name=u'Danish krone', symbol=u'kr.'),
        core.Currency(isocode='DOP', name=u'Dominican peso', symbol=u'$'),
        core.Currency(isocode='DZD', name=u'Algerian dinar', symbol=u'DA'),
        core.Currency(isocode='EGP', name=u'Egyptian pound', symbol=u'LE'),
        core.Currency(isocode='ETB', name=u'Ethiopian birr', symbol=u'Br'),
        core.Currency(isocode='EUR', name=u'Euro', symbol=u'€'),
        core.Currency(isocode='FJD', name=u'Fiji dollar', symbol=u'$'),
        core.Currency(isocode='FKP', name=u'Falkland Islands pound', symbol=u'£'),
        core.Currency(isocode='GBP', name=u'Pound sterling', symbol=u'£'),
        core.Currency(isocode='GEL', name=u'Georgian lari', symbol=u'GEL'),
        core.Currency(isocode='GHS', name=u'Ghanaian cedi', symbol=u'₵'),
        core.Currency(isocode='GIP', name=u'Gibraltar pound', symbol=u'£'),
        core.Currency(isocode='GMD', name=u'Gambian dalasi', symbol=u'D'),
        core.Currency(isocode='GNF', name=u'Guinean franc', symbol=u'FG'),
        core.Currency(isocode='GTQ', name=u'Guatemalan quetzal', symbol=u'Q'),
        core.Currency(isocode='GYD', name=u'Guyanese dollar', symbol=u'$'),
        core.Currency(isocode='HKD', name=u'Hong Kong dollar', symbol=u'$'),
        core.Currency(isocode='HNL', name=u'Honduran lempira', symbol=u'L'),
        core.Currency(isocode='HRK', name=u'Croatian kuna', symbol=u'kn'),
        core.Currency(isocode='HTG', name=u'Haitian gourde', symbol=u'G'),
        core.Currency(isocode='HUF', name=u'Hungarian forint', symbol=u'Ft'),
        core.Currency(isocode='IDR', name=u'Indonesian rupiah', symbol=u'Rp'),
        core.Currency(isocode='ILS', name=u'Israeli new sheqel', symbol=u'₪'),
        core.Currency(isocode='INR', name=u'Indian rupee', symbol=u'₹'),
        core.Currency(isocode='IQD', name=u'Iraqi dinar', symbol=u'د.ع'),
        core.Currency(isocode='IRR', name=u'Iranian rial', symbol=u'﷼'),
        core.Currency(isocode='ISK', name=u'Icelandic króna', symbol=u'kr'),
        core.Currency(isocode='JMD', name=u'Jamaican dollar', symbol=u'$'),
        core.Currency(isocode='JOD', name=u'Jordanian dinar', symbol=u'JD'),
        core.Currency(isocode='JPY', name=u'Japanese yen', symbol=u'¥'),
        core.Currency(isocode='KES', name=u'Kenyan shilling', symbol=u'KSh'),
        core.Currency(isocode='KGS', name=u'Kyrgyzstani som', symbol=u'KGS'),
        core.Currency(isocode='KHR', name=u'Cambodian riel', symbol=u'៛'),
        core.Currency(isocode='KMF', name=u'Comoro franc', symbol=u'CF'),
        core.Currency(isocode='KPW', name=u'North Korean won', symbol=u'₩'),
        core.Currency(isocode='KRW', name=u'South Korean won', symbol=u'₩'),
        core.Currency(isocode='KWD', name=u'Kuwaiti dinar', symbol=u'K.D.'),
        core.Currency(isocode='KZT', name=u'Kazakhstani tenge', symbol=u'₸'),
        core.Currency(isocode='LAK', name=u'Lao kip', symbol=u'₭'),
        core.Currency(isocode='LBP', name=u'Lebanese pound', symbol=u'£'),
        core.Currency(isocode='LKR', name=u'Sri Lankan rupee', symbol=u'₨'),
        core.Currency(isocode='LRD', name=u'Liberian dollar', symbol=u'$'),
        core.Currency(isocode='LSL', name=u'Lesotho loti', symbol=u'L'),
        core.Currency(isocode='LTL', name=u'Lithuanian litas', symbol=u'Lt'),
        core.Currency(isocode='LVL', name=u'Latvian lats', symbol=u'Ls'),
        core.Currency(isocode='LYD', name=u'Libyan dinar', symbol=u'LD'),
        core.Currency(isocode='MAD', name=u'Moroccan dirham', symbol=u'MAD'),
        core.Currency(isocode='MDL', name=u'Moldovan leu', symbol=u'MDL'),
        core.Currency(isocode='MGA', name=u'Malagasy ariary', symbol=u'Ar'),
        core.Currency(isocode='MKD', name=u'Macedonian denar', symbol=u'ден'),
        core.Currency(isocode='MMK', name=u'Myanma kyat', symbol=u'K'),
        core.Currency(isocode='MNT', name=u'Mongolian tugrik', symbol=u'₮'),
        core.Currency(isocode='MOP', name=u'Macanese pataca', symbol=u'MOP$'),
        core.Currency(isocode='MRO', name=u'Mauritanian ouguiya', symbol=u'UM'),
        core.Currency(isocode='MUR', name=u'Mauritian rupee', symbol=u'₨'),
        core.Currency(isocode='MVR', name=u'Maldivian rufiyaa', symbol=u'Rf'),
        core.Currency(isocode='MWK', name=u'Malawian kwacha', symbol=u'MK'),
        core.Currency(isocode='MXN', name=u'Mexican peso', symbol=u'$'),
        core.Currency(isocode='MYR', name=u'Malaysian ringgit', symbol=u'RM'),
        core.Currency(isocode='MZN', name=u'Mozambican metical', symbol=u'MT'),
        core.Currency(isocode='NAD', name=u'Namibian dollar', symbol=u'$'),
        core.Currency(isocode='NGN', name=u'Nigerian naira', symbol=u'₦'),
        core.Currency(isocode='NIO', name=u'Nicaraguan córdoba', symbol=u'C$'),
        core.Currency(isocode='NOK', name=u'Norwegian krone', symbol=u'kr'),
        core.Currency(isocode='NPR', name=u'Nepalese rupee', symbol=u'₨'),
        core.Currency(isocode='NZD', name=u'New Zealand dollar', symbol=u'$'),
        core.Currency(isocode='OMR', name=u'Omani rial', symbol=u'OMR'),
        core.Currency(isocode='PAB', name=u'Panamanian balboa', symbol=u'B/.'),
        core.Currency(isocode='PEN', name=u'Peruvian nuevo sol', symbol=u'S/.'),
        core.Currency(isocode='PGK', name=u'Papua New Guinean kina', symbol=u'K'),
        core.Currency(isocode='PHP', name=u'Philippine peso', symbol=u'₱'),
        core.Currency(isocode='PKR', name=u'Pakistani rupee', symbol=u'₨'),
        core.Currency(isocode='PLN', name=u'Polish złoty', symbol=u'zł'),
        core.Currency(isocode='PYG', name=u'Paraguayan guaraní', symbol=u'₲'),
        core.Currency(isocode='QAR', name=u'Qatari riyal', symbol=u'QR'),
        core.Currency(isocode='RON', name=u'Romanian new leu', symbol=u'RON'),
        core.Currency(isocode='RSD', name=u'Serbian dinar', symbol=u'РСД'),
        core.Currency(isocode='RUB', name=u'Russian rouble', symbol=u'руб.'),
        core.Currency(isocode='RWF', name=u'Rwandan franc', symbol=u'FRw'),
        core.Currency(isocode='SAR', name=u'Saudi riyal', symbol=u'SR'),
        core.Currency(isocode='SBD', name=u'Solomon Islands dollar', symbol=u'$'),
        core.Currency(isocode='SCR', name=u'Seychelles rupee', symbol=u'SR'),
        core.Currency(isocode='SDG', name=u'Sudanese pound', symbol=u'SDG'),
        core.Currency(isocode='SEK', name=u'Swedish krona', symbol=u'kr'),
        core.Currency(isocode='SGD', name=u'Singapore dollar', symbol=u'$'),
        core.Currency(isocode='SHP', name=u'Saint Helena pound', symbol=u'£'),
        core.Currency(isocode='SLL', name=u'Sierra Leonean leone', symbol=u'Le'),
        core.Currency(isocode='SOS', name=u'Somali shilling', symbol=u'Sh.So'),
        core.Currency(isocode='SRD', name=u'Surinamese dollar', symbol=u'$'),
        core.Currency(isocode='STD', name=u'São Tomé and Príncipe dobra', symbol=u'Db'),
        core.Currency(isocode='SYP', name=u'Syrian pound', symbol=u'LS'),
        core.Currency(isocode='SZL', name=u'Swazi lilangeni', symbol=u'L'),
        core.Currency(isocode='THB', name=u'Thai baht', symbol=u'฿'),
        core.Currency(isocode='TJS', name=u'Tajikistani somoni', symbol=u'TJS'),
        core.Currency(isocode='TMT', name=u'Turkmenistani manat', symbol=u'm'),
        core.Currency(isocode='TND', name=u'Tunisian dinar', symbol=u'DT'),
        core.Currency(isocode='TOP', name=u'Tongan paʻanga', symbol=u'T$'),
        core.Currency(isocode='TRY', name=u'Turkish lira', symbol=u'TL'),
        core.Currency(isocode='TTD', name=u'Trinidad and Tobago dollar', symbol=u'$'),
        core.Currency(isocode='TWD', name=u'New Taiwan dollar', symbol=u'NT$'),
        core.Currency(isocode='TZS', name=u'Tanzanian shilling', symbol=u'TZS'),
        core.Currency(isocode='UAH', name=u'Ukrainian hryvnia', symbol=u'₴'),
        core.Currency(isocode='UGX', name=u'Ugandan shilling', symbol=u'USh'),
        core.Currency(isocode='USD', name=u'United States dollar', symbol=u'$'),
        core.Currency(isocode='UYI', name=u'Uruguay Peso en Unidades Indexadas', symbol=u'UYI'),
        core.Currency(isocode='UYU', name=u'Uruguayan peso', symbol=u'$'),
        core.Currency(isocode='UZS', name=u'Uzbekistan som', symbol=u'som'),
        core.Currency(isocode='VEF', name=u'Venezuelan bolívar fuerte', symbol=u'Bs.F.'),
        core.Currency(isocode='VND', name=u'Vietnamese đồng', symbol=u'₫'),
        core.Currency(isocode='VUV', name=u'Vanuatu vatu', symbol=u'VT'),
        core.Currency(isocode='WST', name=u'Samoan tala', symbol=u'WS$'),
        core.Currency(isocode='XAF', name=u'CFA franc BEAC', symbol=u'FCFA'),
        core.Currency(isocode='XCD', name=u'East Caribbean dollar', symbol=u'$'),
        core.Currency(isocode='XOF', name=u'CFA Franc BCEAO', symbol=u'CFA'),
        core.Currency(isocode='XPF', name=u'CFP franc', symbol=u'F'),
        core.Currency(isocode='YER', name=u'Yemeni rial', symbol=u'YER'),
        core.Currency(isocode='ZAR', name=u'South African rand', symbol=u'R'),
        core.Currency(isocode='ZMK', name=u'Zambian kwacha', symbol=u'ZK'),
        core.Currency(isocode='ZWL', name=u'Zimbabwe dollar', symbol=u'$')
    ))
    db.session.commit()

if __name__ == '__main__':
    db.init_db()

    populate_currencies()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'testdb':
            populate_test_db()
