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

import json
import urllib
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import unittest

from ospfm_core.models import Currency, UserContact, UserProfile


OPEN_EXCHANGE_RATES_LATEST_VALUES_URL = (
    'https://raw.github.com/currencybot/open-exchange-rates/master/latest.json'
)


class CurrencyTestCase(unittest.TestCase):

    def test_global_currency_rate_refused(self):
        """Check that a global currency with a static rate is refused"""
        currency = Currency(symbol='XX', rate='1')
        with self.assertRaises(ValidationError):
            currency.full_clean()

    def test_global_currency_name_refused(self):
        """Check that a global currency with a static name is refused"""
        currency = Currency(name='test_global_currency_rate_refused',
                            symbol='XX')
        with self.assertRaises(ValidationError):
            currency.full_clean()

    def test_user_currency_name_forced(self):
        """Check that a user currency has a name"""
        user = User.objects.create(username="test_user_currency_name_forced")
        currency = Currency(owner=user, symbol='XX', rate='1')
        with self.assertRaises(ValidationError):
            currency.full_clean()

    def test_user_currency_rate_forced(self):
        """Check that a user currency has a rate"""
        user = User.objects.create(username="test_user_currency_rate_forced")
        currency = Currency(owner=user, name='test_user_currency_rate_forced',
                            symbol='XX')
        with self.assertRaises(ValidationError):
            currency.full_clean()

    def test_user_currency_can_have_rate(self):
        """Check that a suer currency can be created with a rate"""
        user = User.objects.create(username="test_user_currency_can_have_rate")
        currency = Currency(owner=user,
                            name="test_user_currency_can_have_rate",
                            symbol='TUCHR', rate='1')
        currency.full_clean()
        currency.save()
        self.assertIn(currency, Currency.objects.all())

    def test_user_currency_can_have_no_rate(self):
        """Check that a user currency can be created without a rate"""
        user = User.objects.create(
                username="test_user_currency_can_have_no_rate"
        )
        currency = Currency(owner=user,
                            name="test_user_currency_can_have_no_rate",
                            symbol='TUCCN', rate='1')
        currency.full_clean()
        currency.save()
        self.assertIn(currency, Currency.objects.all())

    def test_global_currencies_exchange_rate(self):
        """Check the exchange rate calculation within global currencies"""
        euro = Currency(symbol='EUR')
        yen = Currency(symbol='JPY')
        allrates_json = urllib.urlopen(OPEN_EXCHANGE_RATES_LATEST_VALUES_URL)
        rates = json.load(allrates_json)
        allrates_json.close()
        eurorate = Decimal(str(rates['rates']['EUR']))
        yenrate = Decimal(str(rates['rates']['JPY']))
        self.assertEqual(yen.get_rate(euro), eurorate / yenrate)

    def test_user_currencies_exchange_rate(self):
        """Check the exchange rate calculation within user currencies"""
        user = User.objects.create(
                username='test_user_currencies_exchange_rate'
        )
        currency1 = Currency(symbol='UCER1')
        currency1.full_clean()
        currency1.save()
        profile = user.get_profile()
        profile.preferred_currency = currency1
        profile.theme = 'no'
        profile.language = 'no'
        profile.full_clean()
        profile.save()
        currency2 = Currency(owner=user,
                             name='test_user_currencies_exchange_rate_2',
                             symbol='UCER2', rate='24')
        currency2.full_clean()
        currency3 = Currency(owner=user,
                             name='test_user_currencies_exchange_rate_2',
                             symbol='UCER3', rate='12.6')
        currency3.full_clean()
        self.assertEqual(currency2.get_rate(currency3), Decimal('0.525'))

    def test_exchange_rate_global_user(self):
        """Check rate calculation with global and user-defined currencies mix"""
        euro = Currency(symbol='EUR')
        euro.full_clean()
        euro.save()
        pound = Currency(symbol='GBP')
        user = User.objects.create(username='test_exchange_rate_global_user')
        currency = Currency(owner=user, name='test_exchange_rate_global_user',
                            symbol='TERGU', rate='9')
        currency.full_clean()
        profile = user.get_profile()
        profile.preferred_currency = euro
        profile.theme = 'no'
        profile.language = 'no'
        profile.full_clean()
        profile.save()
        allrates_json = urllib.urlopen(OPEN_EXCHANGE_RATES_LATEST_VALUES_URL)
        rates = json.load(allrates_json)
        allrates_json.close()
        eurorate = Decimal(str(rates['rates']['EUR']))
        poundrate = Decimal(str(rates['rates']['GBP']))
        europound = poundrate / eurorate
        self.assertEqual(currency.get_rate(pound), europound / currency.rate)
        self.assertEqual(pound.get_rate(currency), currency.rate / europound)

    def test_rate_changed_with_preferred_currency(self):
        """Check that user-defined rates are changed with preferred currency"""
        euro = Currency(symbol='EUR')
        euro.full_clean()
        euro.save()
        dollar = Currency(symbol='USD')
        dollar.full_clean()
        dollar.save()
        user = User.objects.create(
                username='test_rate_changed_with_preferred_currency'
        )
        profile = user.get_profile()
        profile.preferred_currency = euro
        profile.theme = 'no'
        profile.language = 'no'
        profile.full_clean()
        profile.save()
        allrates_json = urllib.urlopen(OPEN_EXCHANGE_RATES_LATEST_VALUES_URL)
        rates = json.load(allrates_json)
        allrates_json.close()
        currency = Currency(owner=user,
                            name='test_rate_changed_with_preferred_currency',
                            symbol='RCWPC', rate='12')
        currency.full_clean()
        currency.save()
        profile.preferred_currency = dollar
        profile.full_clean()
        profile.save()
        currency = Currency.objects.get(owner=user, symbol='RCWPC')
        eurorate = Decimal(str(rates['rates']['EUR']))
        dollarrate = Decimal(str(rates['rates']['USD']))
        self.assertAlmostEqual(currency.rate, 12 * dollarrate / eurorate, 4)


class UserProfileTestCase(unittest.TestCase):

    def test_user_creation(self):
        """Check that a user can be created without error"""
        user = User.objects.create(username="test_profilecreation")
        userid = user.id
        profile = UserProfile.objects.filter(user_id=userid)
        self.assertEqual(profile.count(), 1)
        user.delete()
        profile = UserProfile.objects.filter(user_id=userid)
        self.assertEqual(profile.count(), 0)

    def test_not_userdefined_user_currency_as_default(self):
        """Check a user cannot set a user-defined currency as preferred"""
        user = User.objects.create(
                    username="test_not_another_user_currency_as_default"
        )
        currency = Currency.objects.create(
                        owner=user,
                        name='test_not_another_user_currency_as_default',
                        symbol='TNAUC'
        )
        profile = user.get_profile()
        profile.preferred_currency = currency
        profile.theme = 'no'
        profile.language = 'no'
        with self.assertRaises(ValidationError):
            profile.full_clean()


class UserContactTestCase(unittest.TestCase):

    def test_not_own_contactlist(self):
        """Check that a user cannot put himself in his contactlist"""
        user1 = User.objects.create(username="test_not_own_contactlist_user1")
        contact = UserContact(user=user1, contact=user1)
        with self.assertRaises(ValidationError):
            contact.full_clean()


    def test_contactlist(self):
        """Check that a user can put another in his contact list, only once"""
        user1 = User.objects.create(username="test_contactlist_user1")
        user2 = User.objects.create(username="test_contactlist_user2")
        contact = UserContact(user=user1, contact=user2)
        contact.full_clean()
        contact.save()
        self.assertIn(contact, UserContact.objects.all())
        contact = UserContact(user=user1, contact=user2)
        with self.assertRaises(ValidationError):
            contact.full_clean()
