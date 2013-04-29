#    Copyright 2012-2013 Sebastien Maccagnoni-Munch
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

from ospfm import db, helpers
from ospfm.core import models
from ospfm.transaction import models as transaction
from ospfm.objects import Object

class Currency(Object):

    def __own_currency(self, isocode):
        return models.Currency.query.filter(
            db.and_(
                models.Currency.isocode == isocode,
                db.or_(
                    models.Currency.owner_username == self.username,
                    models.Currency.owner_username == None,
                )
            )
        )

    def list(self):
        currencies = models.Currency.query.filter(
            db.or_(
                models.Currency.owner_username == self.username,
                models.Currency.owner_username == None,
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
        db.session.add(c)
        db.session.commit()
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

        if 'symbol' in self.args:
            # With user-defined currencies, isocode=symbol
            newsymbol = self.args['symbol']
            testcurrency = self.__own_currency(newsymbol).first()
            if not testcurrency:
                currency.isocode = newsymbol
                currency.symbol = newsymbol
        if 'name' in self.args:
            currency.name = self.args['name']
        if 'rate' in self.args:
            currency.rate = self.args['rate']
            self.add_to_response('totalbalance')
        db.session.commit()
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
        db.session.delete(currency)
        db.session.commit()

    def http_rate(self, fromisocode, toisocode):
        response = helpers.rate(self.username, fromisocode, toisocode)
        if response:
            return jsonify(
                        status=200,
                        response=response
                )
        else:
            self.badrequest()
