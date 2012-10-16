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
from sqlalchemy import and_, or_, func

from ospfm.core import exchangerate, models
from ospfm.database import session
from ospfm.transaction import models as transaction
from ospfm.objects import Object

class Currency(Object):

    def __own_currency(self, isocode):
        return models.Currency.query.filter(
            and_(
                models.Currency.isocode == isocode,
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
        # With user-defined currencies, isocode=symbol
        symbol = self.args['symbol']

        currency_exists = self.__own_currency(symbol).all()
        if currency_exists:
            self.badrequest()
        c = models.Currency(
                owner_username = self.username,
                isocode = symbol,
                symbol = symbol,
                name = self.args['name'],
                rate = self.args['rate']
        )
        session.add(c)
        session.commit()
        return c.as_dict()

    def read(self, isocode):
        currency = self.__own_currency(isocode).first()
        if currency:
            return currency.as_dict(with_rate=True)
        else:
            self.notfound()

    def update(self, isocode):
        currency = self.__own_currency(isocode).first()
        if not currency:
            self.notfound()
        if not currency.owner_username:
            self.forbidden()

        if self.args.has_key('symbol'):
            # With user-defined currencies, isocode=symbol
            newsymbol = self.args['symbol']
            testcurrency = self.__own_currency(newsymbol).first()
            if not testcurrency:
                currency.isocode = newsymbol
                currency.symbol = newsymbol
        if self.args.has_key('name'):
            currency.name = self.args['name']
        if self.args.has_key('rate'):
            currency.rate = self.args['rate']
        session.commit()
        return currency.as_dict()

    def delete(self, isocode):
        currency = self.__own_currency(isocode).first()
        if not currency:
            self.notfound()
        if not currency.owner_username:
            self.forbidden()
        # Only delete the currency if it is not in use
        if transaction.Account.query.filter(
                transaction.Account.currency == currency
           ).count() or \
           transaction.Category.query.filter(
                transaction.Category.currency == currency
           ).count() or \
           transaction.Transaction.query.filter(
                transaction.Account.currency == currency
           ).count():
                self.badrequest()
        session.delete(currency)
        session.commit()

    def rate(self, fromisocode, toisocode):
        if fromisocode == toisocode:
            return 1
        # Initialize the username so we can request the currencies
        # XXX May be improved if, one day, this is used outside an HTTP request
        self._Object__init_http()
        # Request the currencies
        fromcurrency = self.__own_currency(fromisocode).first()
        tocurrency = self.__own_currency(toisocode).first()
        if not fromcurrency or not tocurrency:
            self.badrequest()
        # Both currencies are globally defined
        if (not fromcurrency.rate) and (not tocurrency.rate):
            return exchangerate.getrate(fromcurrency.isocode, tocurrency.isocode)
        # Both currencies are user-defined
        elif fromcurrency.rate and tocurrency.rate:
            return tocurrency.rate / fromcurrency.rate
        # Mixed user-defined / globally defined rates
        else:
            preferred_isocode = models.User.query.filter(
                                    models.User.username==self.username
                               ).one().preferred_currency.isocode
            # From a user-defined currency to a globally defined currency
            if fromcurrency.rate and (not tocurrency.rate):
                target_rate = exchangerate.getrate(preferred_isocode,
                                                   tocurrency.isocode)
                return target_rate / fromcurrency.rate
            if (not fromcurrency.rate) and tocurrency.rate:
                source_rate = exchangerate.getrate(preferred_isocode,
                                                   fromcurrency.isocode)
                return tocurrency.rate / source_rate
        # This should not happen
        self.badrequest()

    def http_rate(self, fromisocode, toisocode):
        return jsonify(
                    status=200,
                    response=self.rate(fromisocode, toisocode)
               )
