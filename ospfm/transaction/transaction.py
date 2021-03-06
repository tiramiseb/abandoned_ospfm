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

import datetime, json

from flask import jsonify

from ospfm import db, helpers
from ospfm.core import currency
from ospfm.core import models as core
from ospfm.transaction import models
from ospfm.objects import Object


class Transaction(Object):

    def __own_transaction(self, transactionid):
        return models.Transaction.query.options(
                          db.joinedload(models.Transaction.currency),
                          db.joinedload(models.Transaction.transaction_accounts),
                          db.joinedload(models.Transaction.transaction_categories)
               ).filter(
                    db.and_(
                        models.Transaction.owner_username == self.username,
                        models.Transaction.id == transactionid
                    )
               ).first()

    def list(self):
        # Transactions cannot be listed with the API
        self.forbidden('Listing all transactions is forbidden')

    def create(self):
        if not (
            'currency' in self.args and \
            'date' in self.args and \
            'description' in self.args and \
            'amount' in self.args
        ):
            self.badrequest(
           "Please provide transaction description, currency, amount and date")
        # First, create the transaction object
        currency = core.Currency.query.filter(
            db.and_(
                core.Currency.isocode == self.args['currency'],
                db.or_(
                    core.Currency.owner_username == self.username,
                    core.Currency.owner_username == None
                )
            )
        ).first()
        if not currency:
            self.badrequest("This currency does not exist")
        date = helpers.date_from_string(self.args['date'])
        if not date:
            self.badrequest("This date cannot be understood")
        description = self.args['description']
        if 'original_description' in self.args:
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
        db.session.add(transaction)

        # Next, create the links from the transaction to its accounts
        if 'accounts' in self.args:
            accounts = json.loads(self.args['accounts'])
            for accountdata in accounts:
                transaction_accounts = []
                if 'amount' in accountdata:
                    # If no amount is specified, do not associate the account
                    accountobject = models.Account.query.options(
                        db.joinedload(models.Account.account_owners)
                    ).filter(
                        db.and_(
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
                        db.session.add(ta)
                    self.add_to_response('accountbalance',
                                         accountdata['account'])
            self.add_to_response('totalbalance')

        # Next, create the links from the transaction to its categories
        if 'categories' in self.args:
            categories = json.loads(self.args['categories'])
            for categorydata in categories:
                transaction_categories = []
                if 'transaction_amount' in categorydata and \
                   'category_amount' in categorydata:
                    # If no amount is specified, do not associate the category
                    categoryobject = models.Category.query.options(
                        db.joinedload(models.Category.currency)
                    ).filter(
                        db.and_(
                            models.Category.id == categorydata['category'],
                            models.Category.owner_username == self.username,
                        )
                    ).first()
                    if categoryobject:
                        tc = models.TransactionCategory(
                                transaction = transaction,
                                category = categoryobject,
                       transaction_amount = categorydata['transaction_amount'],
                              category_amount = categorydata['category_amount']
                        )
                        db.session.add(tc)
                    self.add_to_response('categoriesbalance',
                                         categorydata['category'])

        # Commit everything...
        db.session.commit()
        return transaction.as_dict(self.username)

    def read(self, transactionid):
        transaction = self.__own_transaction(transactionid)
        if transaction:
            return transaction.as_dict(self.username)
        self.notfound('This transaction does not exist or you do not own it')

    def update(self, transactionid):
        transaction = self.__own_transaction(transactionid)
        if not transaction:
            self.notfound(
           'Nonexistent transaction cannot be modified (or you do not own it)')

        # First, modifications on the Transaction object itself
        if 'description' in self.args:
            desc = self.args['description']
            if desc.strip() == '':
                transaction.description = transaction.original_description
            else:
                transaction.description = desc
        if 'amount' in self.args:
            transaction.amount = self.args['amount']
        if 'currency' in self.args:
            currency = core.Currency.query.filter(
                db.and_(
                    core.Currency.isocode == self.args['currency'],
                    db.or_(
                        core.Currency.owner_username == self.username,
                        core.Currency.owner_username == None
                    )
                )
            ).first()
            if currency:
                transaction.currency = currency
        if 'date' in self.args:
            date = helpers.date_from_string(self.args['date'])
            if date:
                transaction.date = date

        # Next, update accounts
        if 'accounts' in self.args:
            existing_accounts = dict([ta.as_tuple() for ta in
                                      transaction.transaction_accounts])
            new_accounts_data = json.loads(self.args['accounts'])
            for account_data in new_accounts_data:
                if 'amount' in account_data and 'account' in account_data:
                    amount = account_data['amount']
                    accountid = account_data['account']
                    if accountid in existing_accounts.keys():
                        # Account already linked...
                        if existing_accounts[accountid] != amount:
                            # ...but the amount is different
                            ta = models.TransactionAccount.query.filter(db.and_(
                          models.TransactionAccount.transaction == transaction,
                          models.TransactionAccount.account_id == accountid
                            )).one()
                            ta.amount = amount
                            ta.verified = False
                            self.add_to_response('accountbalance', accountid)
                        existing_accounts.pop(accountid)
                    else:
                        # Account is not already linked
                        # Verify the account is owned by the user
                        accountobject = models.Account.query.options(
                            db.joinedload(models.Account.account_owners)
                        ).filter(
                          db.and_(
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
                            self.add_to_response('accountbalance', accountid)
                            db.session.add(ta)
            # All accounts to keep have been poped out from "existing_accounts"
            # Delete all links remaining from this transaction to accounts
            for accountid in existing_accounts.keys():
                ta = models.TransactionAccount.query.filter(db.and_(
                    models.TransactionAccount.transaction == transaction,
                    models.TransactionAccount.account_id == accountid
                )).one()
                self.add_to_response('accountbalance', accountid)
                db.session.delete(ta)

            self.add_to_response('totalbalance')

        # Then, update categories
        if 'categories' in self.args:
            existing_categories = dict([tc.as_tuple() for tc in
                                        transaction.transaction_categories])
            new_categories_data = json.loads(self.args['categories'])
            for category_data in new_categories_data:
                if 'transaction_amount' in category_data and \
                   'category_amount' in category_data and \
                   'category' in category_data:
                    transaction_amount = category_data['transaction_amount']
                    category_amount = category_data['category_amount']
                    categoryid = category_data['category']
                    if categoryid in existing_categories.keys():
                        # Category already linked...
                        if existing_categories[categoryid]['category_amount'] \
                           != category_amount:
                            # ...but the amount is different
                            tc = models.TransactionCategory.query.filter(db.and_(
                         models.TransactionCategory.transaction == transaction,
                         models.TransactionCategory.category_id == categoryid
                            )).one()
                            tc.transaction_amount = transaction_amount
                            tc.category_amount = category_amount
                            tc.verified = False
                            self.add_to_response('categoriesbalance',
                                                 categoryid)
                        existing_categories.pop(categoryid)
                    else:
                        # Category is not already linked
                        # Verify the category is owned by the user
                        categoryobject = models.Category.query.filter(
                          db.and_(
                           models.Category.id == categoryid,
                           models.Category.owner_username == self.username
                         )
                        ).first()
                        if categoryobject:
                            tc = models.TransactionCategory(
                                    transaction = transaction,
                                    category = categoryobject,
                                    transaction_amount = transaction_amount,
                                    category_amount = category_amount
                            )
                            self.add_to_response('categoriesbalance',
                                                 categoryid)
                            db.session.add(tc)
            # All categories to keep have been poped out from
            # "existing_categories"
            # Delete all links remaining from this transaction to categories
            for categoryid in existing_categories.keys():
                tc = models.TransactionCategory.query.filter(db.and_(
                    models.TransactionCategory.transaction == transaction,
                    models.TransactionCategory.category_id == categoryid
                )).one()
                self.add_to_response('categoriesbalance', categoryid)
                db.session.delete(tc)

        db.session.commit()
        return transaction.as_dict(self.username)

    def delete(self, transactionid):
        transaction = self.__own_transaction(transactionid)
        if not transaction:
            self.notfound(
            'Nonexistent transaction cannot be deleted (or you do not own it)')
        self.add_to_response('totalbalance')
        for ta in transaction.transaction_accounts:
            self.add_to_response('accountbalance', ta.account_id)
        for tc in transaction.transaction_categories:
            self.add_to_response('categoriesbalance', tc.category_id)
        db.session.delete(transaction)
        db.session.commit()

    def http_filter(self):
        self._Object__init_http()
        return jsonify(status=200, response=self.__filter(self.args))

    def __filter(self, filter):
        filters = [
            models.Transaction.owner_username == self.username,
        ]
        limit = 100
        after = False
        for part in filter.items():
            if part[0] in filter_functions:
                filters.extend(
                    filter_functions[part[0]](part[1])
                )
            elif part[0] == 'limit':
                try:
                    limit = min(int(part[1]), 100)
                except:
                    pass
            elif part[0] == 'after':
                try:
                    after = int(part[1])
                except:
                    pass
        if after:
            # Get offset of the "from" transaction
            # XXX: Is there a more efficient way to do so ?
            all_transactions = db.session.query(models.Transaction.id).order_by(
                                db.desc(models.Transaction.date)
                           ).filter(
                                db.and_(
                                    *filters
                                )
                           )
            all_ids = [t.id for t in all_transactions]
            try:
                offset = all_ids.index(after) + 1
            except:
                offset = 0
            transactions = models.Transaction.query.options(
                        db.joinedload(models.Transaction.currency),
                        db.joinedload(models.Transaction.transaction_accounts),
                        db.joinedload(models.Transaction.transaction_categories)
                    ).order_by(
                        db.desc(models.Transaction.date)
                    ).filter(
                        db.and_(
                            *filters
                        )
                    ).offset(offset).limit(limit)
            return [t.as_dict(self.username) for t in transactions]
        else:
            transactions = models.Transaction.query.options(
                        db.joinedload(models.Transaction.currency),
                        db.joinedload(models.Transaction.transaction_accounts),
                        db.joinedload(models.Transaction.transaction_categories)
                    ).order_by(
                        db.desc(models.Transaction.date)
                    ).filter(
                        db.and_(
                            *filters
                        )
                    ).limit(limit)
            return [t.as_dict(self.username) for t in transactions]

def account_filter(value):
    return [
        models.Transaction.id == models.TransactionAccount.transaction_id,
        models.TransactionAccount.account_id == value
    ]
def category_filter(value):
    def subcategories(categoryid, categorylist):
        for cat in models.Category.query.filter(
                        models.Category.parent_id == categoryid
                    ):
            categorylist.append(cat.id)
            categorylist = subcategories(cat.id, categorylist)
        return categorylist

    categorylist = subcategories(value, [ int(value) ])
    return [
        models.Transaction.id == models.TransactionCategory.transaction_id,
        db.or_(*[ models.TransactionCategory.category_id == value \
               for value in categorylist ])
    ]
def currency_filter(value):
    return [
        models.Transaction.currency_id == core.Currency.id,
        core.Currency.isocode == value
    ]
def dates_filter(value):
    try:
        f = []
        fromdate, todate = value.split('-')
        if fromdate:
            f.append(
                models.Transaction.date >= datetime.date(
                                                int(fromdate[:4]),
                                                int(fromdate[4:6]),
                                                int(fromdate[6:])
                                            )
            )
        if todate:
            f.append(
                models.Transaction.date <= datetime.date(
                                                int(todate[:4]),
                                                int(todate[4:6]),
                                                int(todate[6:])
                                            )
            )
        return f
    except:
        return []

filter_functions = {
    'account': account_filter,
    'category': category_filter,
    'currency': currency_filter,
    'dates': dates_filter
}
