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

import datetime

from flask import request
from sqlalchemy import and_, or_

from ospfm import config
from ospfm.core import exchangerate
from ospfm.core import models as core

def flask_get_username():
    # remote_user contains the user's username when (s)he is authorized by the server
    if request.remote_user:
        return request.remote_user
    if config.DEVEL:
        return config.DEVEL_USERNAME
    return None

def date_from_string(string):
    # Convert a "YYYY-MM-DD" string to a date
    if len(string) == 10:
        try:
            return datetime.date(
                        int(string[:4]),
                        int(string[5:7]),
                        int(string[8:])
            )
        except:
            pass
    return None

def rate(fromisocode, toisocode):
    if fromisocode == toisocode:
        return 1
    username = flask_get_username()
    # Request the currencies
    fromcurrency = core.Currency.query.filter(
        and_(
            core.Currency.isocode == fromisocode,
            or_(
                core.Currency.owner_username == username,
                core.Currency.owner == None,
            )
        )
    ).first()
    tocurrency = core.Currency.query.filter(
        and_(
            core.Currency.isocode == toisocode,
            or_(
                core.Currency.owner_username == username,
                core.Currency.owner == None,
            )
        )
    ).first()
    if not fromcurrency or not tocurrency:
        return None
    # Both currencies are globally defined
    if (fromcurrency.rate is None) and (tocurrency.rate is None):
        return exchangerate.getrate(fromcurrency.isocode, tocurrency.isocode)
    # Both currencies are user-defined
    elif (fromcurrency.rate is not None) and (tocurrency.rate is not None):
        return tocurrency.rate / fromcurrency.rate
    # Mixed user-defined / globally defined rates
    else:
        preferred_isocode = core.User.query.filter(
                                core.User.username==username
                           ).one().preferred_currency.isocode
        # From a user-defined currency to a globally defined currency
        if (fromcurrency.rate is not None) and (tocurrency.rate is None):
            target_rate = exchangerate.getrate(preferred_isocode,
                                               tocurrency.isocode)
            if (fromcurrency.rate == 0):
                return 0
            return target_rate / fromcurrency.rate
        if (fromcurrency.rate is None) and (tocurrency.rate is not None):
            source_rate = exchangerate.getrate(preferred_isocode,
                                               fromcurrency.isocode)
            if (tocurrency.rate == 0):
                return 0
            return tocurrency.rate / source_rate
