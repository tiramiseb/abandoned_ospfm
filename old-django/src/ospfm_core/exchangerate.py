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

import time
import json
import urllib
from decimal import Decimal

from django.core.cache import cache

OPEN_EXCHANGE_RATES_LATEST_VALUES_URL = (
    'http://openexchangerates.org/latest.json'
)

def getrate(from_currency, to_currency, amount='1'):
    # Using "Decimal(str(<value>))" in order to get exact results
    rates = cache.get('open-exchange-rates')
    if not rates:
        exchanges_json = urllib.urlopen(OPEN_EXCHANGE_RATES_LATEST_VALUES_URL)
        rates = json.load(exchanges_json)
        exchanges_json.close()
        # In order to have the most up-to-date rates from OpenExchangeRates,
        # duration = 1 hour - (now - timestamp) + 10 seconds security window)
        duration = 3600 - (int(time.time()) - rates['timestamp']) + 10
        cache.set('open-exchange-rates', rates, duration)
    base_to_from = Decimal(str(rates['rates'][from_currency]))
    base_to_to = Decimal(str(rates['rates'][to_currency]))
    # Return the association of both rates
    return base_to_to / base_to_from * Decimal(str(amount))
