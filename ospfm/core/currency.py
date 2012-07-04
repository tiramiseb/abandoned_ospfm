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

from flask import abort, jsonify
from sqlalchemy import and_, or_

from ospfm.core import exchangerate, models
from ospfm.database import session
from ospfm.objects import Object

class Currency(Object):

    def __own_currency(self, symbol):
        return models.Currency.query.filter(
            and_(
                models.Currency.symbol == symbol,
                or_(
                    models.Currency.owner_username == self.username,
                    models.Currency.owner == None,
                )
            )
        )

    def list(self):
        currencies = models.Currency.query.filter(
            or_(
                models.Currency.owner_username == self.username,
                models.Currency.owner == None,
            )
        )
        return [c.as_dict() for c in currencies]

    def create(self):
        symbol = self.args['symbol']

        currency_exists = self.__own_currency(symbol).all()
        if currency_exists:
            self.badrequest()
        else:
            c = models.Currency(
                    owner_username = self.username,
                    symbol = symbol,
                    name = self.args['name'],
                    rate = self.args['rate']
            )
            session.add(c)
            session.commit()
            return c.as_dict()

    def read(self, symbol):
        currency = self.__own_currency(symbol).first()
        if currency:
            return currency.as_dict(with_rate=True)
        else:
            self.notfound()

    def update(self, symbol):
        currency = self.__own_currency(symbol).first()
        if not currency:
            self.notfound()
        if not currency.owner_username:
            self.forbidden()

        if self.args.has_key('symbol'):
            currency.symbol = self.args['symbol']
        if self.args.has_key('name'):
            currency.name = self.args['name']
        if self.args.has_key('rate'):
            currency.rate = self.args['rate']

        return currency.as_dict()

    def delete(self, symbol):
        # XXX Only delete the currency if it is not in use
        currency = self.__own_currency(symbol).first()
        if not currency:
            self.notfound()
        if not currency.owner_username:
            self.forbidden()
        session.delete(currency)

    def __rate(self, fromsymbol, tosymbol):
        fromcurrency = self.__own_currency(fromsymbol).first()
        tocurrency = self.__own_currency(tosymbol).first()
        if not fromcurrency or not tocurrency:
            self.badrequest()
        # Both currencies are globally defined
        if (not fromcurrency.rate) and (not tocurrency.rate):
            return exchangerate.getrate(fromcurrency.symbol, tocurrency.symbol)
        # Both currencies are user-defined
        elif fromcurrency.rate and tocurrency.rate:
            return tocurrency.rate / fromcurrency.rate
        # Mixed user-defined / globally defined rates
        else:
            preferred_symbol = models.User.query.filter(
                                    username=self.username
                               ).one().preferred_currency
            # From a user-defined currency to a globally defined currency
            if fromcurrency.rate and (not tocurrency.rate):
                target_rate = exchangerate.getrate(preferred_symbol,
                                                   tocurrency.symbol)
                return target_rate / fromcurrency.rate
            if (not fromcurrency.rate) and tocurrency.rate:
                source_rate = exchangerate.getrate(preferred_symbol,
                                                   fromcurrency.symbol)
                return tocurrency.rate / source_rate
        # This should not happen
        self.badrequest()

    def http_rate(self, fromsymbol, tosymbol):
        self._Object__init_http()
        return jsonify(status=200, response=self.__rate(fromsymbol, tosymbol))
