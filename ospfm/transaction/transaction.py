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

from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from ospfm import helpers
from ospfm.core import currency
from ospfm.core import models as core
from ospfm.transaction import models
from ospfm.database import session
from ospfm.objects import Object


class Transaction(Object):

    def __own_transaction(self, transactionid):
        return models.Transaction.query.options(
                          joinedload(models.Transaction.currency),
                          joinedload(models.Transaction.transaction_accounts),
                          joinedload(models.Transaction.transaction_categories)
               ).filter(
                    and_(
                        models.Transaction.owner_username == self.username,
                        models.Transaction.id == transactionid
                    )
               ).first()

    def list(self):
        # XXX Listing all transactions will probably disappear,
        #     replaced by some sort of search filter
        transactions = models.Transaction.query.options(
                          joinedload(models.Transaction.currency),
                          joinedload(models.Transaction.transaction_accounts),
                          joinedload(models.Transaction.transaction_categories)
                       ).order_by(
                            models.Transaction.date
                       ).filter(
                            models.Transaction.owner_username == self.username
                       ).all()
        return [t.as_dict() for t in transactions]

    def create(self):
        # First, create the transaction object
        currency = core.Currency.query.filter(
            and_(
                core.Currency.isocode == self.args['currency'],
                or_(
                    core.Currency.owner_username == self.username,
                    core.Currency.owner == None
                )
            )
        ).first()
        if not currency:
            self.badrequest()
        date = helpers.date_from_string(self.args['date'])
        if not date:
            self.badrequest()
        description = self.args['description']
        if self.args.has_key('original_description'):
            original_description = self.args['original_description']
        else:
            original_description = description
        transaction = models.Transaction(
            owner_username = self.username,
            description = description,
            original_description = original_description,
            amount = self.args['amount'],
            currency = currency,
            date = date
        )
        session.add(transaction)

        # Next, create the links from the transaction to its accounts
        if self.args.has_key('accounts'):
            accounts = json.loads(self.args['accounts'])
            for accountdata in accounts:
                transaction_accounts = []
                if accountdata.has_key('amount'):
                    # If no amount is specified, do not associate the account
                    accountobject = models.Account.query.options(
                        joinedload(models.Account.account_owners)
                    ).filter(
                        and_(
                           models.Account.id == accountdata['account'],
                           models.AccountOwner.owner_username == self.username,
                        )
                    ).first()
                    if accountobject:
                        ta = models.TransactionAccount(
                                transaction = transaction,
                                account = accountobject,
                                amount = accountdata['amount'],
                                verified = False
                        )
                        session.add(ta)

        # Next, create the links from the transaction to its categories
        if self.args.has_key('categories'):
            categories = json.loads(self.args['categories'])
            for categorydata in categories:
                transaction_categories = []
                if categorydata.has_key('amount'):
                    # If no amount is specified, do not associate the category
                    categoryobject = models.Category.query.options(
                        joinedload(models.Category.currency)
                    ).filter(
                        and_(
                            models.Category.id == accountdata['account'],
                            models.Category.owner_username == self.username,
                        )
                    ).first()
                    if categoryobject:
                        tc = models.TransactionCategory(
                                transaction = transaction,
                                category = categoryobject,
                                amount = categorydata['amount']
                        )
                        session.add(tc)

        # Commit everything...
        session.commit()
        return transaction.as_dict()

    def read(self, transactionid):
        transaction = self.__own_transaction(transactionid)
        if transaction:
            return transaction.as_dict()
        self.notfound()

    def update(self, transactionid):
        transaction = self.__own_transaction(transactionid)
        if not transaction:
            self.notfound()

        # First, modifications on the Transaction object itself
        if self.args.has_key('description'):
            transaction.description = self.args['description']
        if self.args.has_key('amount'):
            transaction.amount = self.args['amount']
        if self.args.has_key('currency'):
            currency = core.Currency.query.filter(
                and_(
                    core.Currency.isocode == self.args['currency'],
                    or_(
                        core.Currency.owner_username == self.username,
                        core.Currency.owner == None
                    )
                )
            ).first()
            if currency:
                transaction.currency = self.args['currency']
        if self.args.has_key('date'):
            date = helpers.date_from_string(self.args['date'])
            if date:
                transaction.date = date

        # Next, update accounts
        if self.args.has_key('accounts'):
            existing_accounts = dict([ta.as_tuple() for ta in
                                      transaction.transaction_accounts])
            new_accounts_data = json.loads(self.args['accounts'])
            for account_data in new_accounts_data:
                if account_data.has_key('amount') and \
                   account_data.has_key('account'):
                    amount = account_data['amount']
                    accountid = account_data['account']
                    if accountid in existing_accounts.keys():
                        # Account already linked...
                        if existing_accounts[accountid] != amount:
                            # ...but the amount is different
                            ta = models.TransactionAccount.query.filter(and_(
                          models.TransactionAccount.transaction == transaction,
                          models.TransactionAccount.account_id == accountid
                            )).one()
                            ta.amount = amount
                            ta.verified = False
                        existing_accounts.pop(accountid)
                    else:
                        # Account is not already linked
                        # Verify the account is owned by the user
                        accountobject = models.Account.query.options(
                            joinedload(models.Account.account_owners)
                        ).filter(
                          and_(
                            models.Account.id == accountid,
                            models.AccountOwner.owner_username == self.username
                         )
                        ).first()
                        if accountobject:
                            ta = models.TransactionAccount(
                                    transaction = transaction,
                                    account = accountobject,
                                    amount = amount,
                                    verified = False
                            )
                            session.add(ta)
            # All accounts to keep have been poped out from "existing_accounts"
            # Delete all links remaining from this transaction to accounts
            for accountid in existing_accounts.keys():
                ta = models.TransactionAccount.query.filter(and_(
                    models.TransactionAccount.transaction == transaction,
                    models.TransactionAccount.account_id == accountid
                )).one()
                session.delete(ta)

        # Then, update categories
        if self.args.has_key('categories'):
            existing_categories = dict([tc.as_tuple() for tc in
                                        transaction.transaction_categories])
            new_categories_data = json.loads(self.args['categories'])
            for category_data in new_categories_data:
                if category_data.has_key('amount') and \
                   category_data.has_key('category'):
                    amount = category_data['amount']
                    categoryid = category_data['category']
                    if categoryid in existing_categories.keys():
                        # Category already linked...
                        if existing_categories[categoryid] != amount:
                            # ...but the amount is different
                            tc = models.TransactionCategory.query.filter(and_(
                         models.TransactionCategory.transaction == transaction,
                         models.TransactionCategory.category_id == categoryid
                            )).one()
                            tc.amount = amount
                            tc.verified = False
                        existing_categories.pop(categoryid)
                    else:
                        # Category is not already linked
                        # Verify the category is owned by the user
                        categoryobject = models.Category.query.filter(
                          and_(
                           models.Category.id == categoryid,
                           models.Category.owner_username == self.username
                         )
                        ).first()
                        if categoryobject:
                            tc = models.TransactionCategory(
                                    transaction = transaction,
                                    category = categoryobject,
                                    amount = amount
                            )
                            session.add(tc)
            # All categories to keep have been poped out from
            # "existing_categories"
            # Delete all links remaining from this transaction to categories
            for categoryid in existing_categories.keys():
                ta = models.TransactionCategory.query.filter(and_(
                    models.TransactionCategory.transaction == transaction,
                    models.TransactionCategory.category_id == categoryid
                )).one()
                session.delete(ta)

        session.commit()
        return transaction.as_dict()

    def delete(self, transactionid):
        transaction = self.__own_transaction(transactionid)
        if not transaction:
            self.notfound()
        session.delete(transaction)
        session.commit()
