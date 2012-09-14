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

from decimal import Decimal

from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from ospfm.core import models as core
from ospfm.core import currency as corecurrency
from ospfm.transaction import models
from ospfm.database import session
from ospfm.objects import Object


class Account(Object):

    def __own_account(self, accountid):
        return models.Account.query.options(
                        joinedload(models.Account.currency)
               ).join(models.AccountOwner).filter(
                    and_(
                        models.AccountOwner.owner_username == self.username,
                        models.Account.id == accountid
                    )
               ).first()

    def list(self):
        accounts = models.Account.query.options(
                        joinedload(models.Account.currency)
        ).join(models.AccountOwner).filter(
            models.AccountOwner.owner_username == self.username
        ).all()
        # Calculate the total balance, in the user's preferred currency
        totalbalance = 0
        totalcurrency = core.User.query.options(
                            joinedload(core.User.preferred_currency)
        ).get(self.username).preferred_currency.symbol
        for account in accounts:
            totalbalance += account.balance() * \
            corecurrency.Currency().rate(account.currency.symbol,
                                         totalcurrency)
        return {
            'accounts': [a.as_dict() for a in accounts],
            'total': {
                'balance': totalbalance,
                'currency': totalcurrency
            }
        }

    def create(self):
        currency = core.Currency.query.filter(
            and_(
                core.Currency.symbol == self.args['currency'],
                or_(
                    core.Currency.owner_username == self.username,
                    core.Currency.owner == None
                )
            )
        ).first()
        if not currency:
            self.badrequest()

        name = self.args['name']
        start_balance = self.args['start_balance']

        a = models.Account(
                name=name,
                currency=currency,
                start_balance=start_balance
        )
        ao = models.AccountOwner(account=a, owner_username=self.username)
        session.add_all((a, ao))
        session.commit()
        return a.as_dict()

    def read(self, accountid):
        account = self.__own_account(accountid)
        if account:
            return account.as_dict()
        self.notfound()

    def update(self, accountid):
        account = self.__own_account(accountid)
        if not account:
            self.notfound()
        if self.args.has_key('name'):
            account.name = self.args['name']
        if self.args.has_key('currency'):
            # Do not update currency if account has transactions
            if not models.TransactionAccount.query.filter(
                        models.TransactionAccount.account == account
                   ).count():
                currency = core.Currency.query.filter(
                    and_(
                        core.Currency.symbol == self.args['currency'],
                        or_(
                            core.Currency.owner_username == self.username,
                            core.Currency.owner == None
                        )
                    )
                ).first()
                if currency:
                    account.currency = currency
        if self.args.has_key('start_balance'):
            account.start_balance = Decimal(self.args['start_balance'])
        return account.as_dict()

    def delete(self, accountid):
        account = self.__own_account(accountid)
        if not account:
            self.notfound()
        session.delete(account)
        session.commit()
