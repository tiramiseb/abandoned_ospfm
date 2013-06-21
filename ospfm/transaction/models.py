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


import datetime

from ospfm import config, db, helpers
from ospfm.core import exchangerate, models as coremodels

cache = config.CACHE



class Account(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(50), nullable=False)
    currency_id   = db.Column(db.ForeignKey('currency.id', ondelete='CASCADE'))
    start_balance = db.Column(db.Numeric(15, 3), nullable=False)

    currency = db.relationship('Currency')

    def __unicode__(self):
        return u'Account id {0}, name "{1}", currency "{2}", start balance {3}'.format(
                    self.id, self.name, self.currency.isocode,
                    self.start_balance
                )

    def balance(self, username):
        """
        Return a list :
            [ <balance in account currency>, <balance in preferred currency> ]
        """
        balance = db.session.query(
            db.func.sum(TransactionAccount.amount)
        ).filter(
            TransactionAccount.account_id == self.id
        ).one()[0]
        if balance:
            balances = [ self.start_balance + balance ]
        else:
            balances = [ self.start_balance ]
        balances.append(
            helpers.rate(
                username,
                self.currency.isocode,
                coremodels.User.query.options(
                    db.joinedload(coremodels.User.preferred_currency)
                ).get(
                    username
                ).preferred_currency.isocode
            ) * balances[0]
        )
        return balances

    def transactions_count(self):
        return db.session.query(
            db.func.count(TransactionAccount.transaction_id)
        ).filter(
            TransactionAccount.account_id == self.id
        ).one()[0] or 0

    def as_dict(self, username, short=False):
        if short:
            return {
                'id': self.id,
                'name': self.name,
                'currency': self.currency.isocode
            }
        else:
            balances = self.balance(username)
            return {
                'id': self.id,
                'name': self.name,
                'currency': self.currency.isocode,
                'start_balance': self.start_balance,
                'balance': balances[0],
                'balance_preferred': balances[1],
                'transactions_count': self.transactions_count()
            }



class AccountOwner(db.Model):
    account_id     = db.Column(db.ForeignKey('account.id', ondelete='CASCADE'),
                               primary_key=True)
    owner_username = db.Column(db.ForeignKey('user.username',
                                             onupdate='CASCADE',
                                             ondelete='CASCADE'),
                               primary_key=True)

    account = db.relationship('Account', backref=db.backref(
                                                   'account_owners',
                                                   cascade="all, delete-orphan"
                                                ))
    owner = db.relationship('User', backref=db.backref('accounts_owner'))



class Category(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    owner_username = db.Column(db.ForeignKey('user.username',
                                             onupdate='CASCADE',
                                             ondelete='CASCADE'),
                               nullable=False)
    parent_id      = db.Column(db.ForeignKey('category.id',
                                             ondelete='SET NULL'))
    currency_id    = db.Column(db.ForeignKey('currency.id',
                                             ondelete='CASCADE'))
    name           = db.Column(db.String(50), nullable=False)

    currency = db.relationship('Currency')

    children = db.relationship('Category', order_by='Category.name',
                               backref=db.backref('parent', remote_side=[id]))

    def __unicode__(self):
        if self.parent_id:
            return u'Category id {0}, name "{1}", parent id {2}'.format(
                        self.id, self.name, self.parent_id
                    )
        else:
            return u'Category id {0}, name "{1}"'.format(self.id, self.name)

    def balance(self, username):
        today = datetime.date.today()

        balance = cache.get('categorybalance-{0}'.format(self.id))

        if not balance:
            balance = {'currency': self.currency.isocode}
            balance['year'] = db.session.query(
                db.func.sum(TransactionCategory.category_amount)
            ).filter(
                db.and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        datetime.date(today.year, 1, 1),
                        datetime.date(today.year, 12, 31)
                    )
                )
            ).one()[0] or 0

            if today.month == 12:
                lastdayofmonth = datetime.date(today.year, 12, 31)
            else:
                lastdayofmonth = datetime.date(today.year, today.month+1, 1) -\
                                                          datetime.timedelta(1)
            balance['month'] = db.session.query(
                db.func.sum(TransactionCategory.category_amount)
            ).filter(
                db.and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        datetime.date(today.year, today.month, 1),
                        lastdayofmonth
                    )
                )
            ).one()[0] or 0

            firstdayofweek = today - datetime.timedelta(today.weekday())
            lastdayofweek = today + datetime.timedelta(6-today.weekday())
            balance['week'] = db.session.query(
                db.func.sum(TransactionCategory.category_amount)
            ).filter(
                db.and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        firstdayofweek,
                        lastdayofweek
                    )
                )
            ).one()[0] or 0

            balance['7days'] = db.session.query(
                db.func.sum(TransactionCategory.category_amount)
            ).filter(
                db.and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        today - datetime.timedelta(6),
                        today
                    )
                )
            ).one()[0] or 0

            balance['30days'] = db.session.query(
                db.func.sum(TransactionCategory.category_amount)
            ).filter(
                db.and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        today - datetime.timedelta(29),
                        today
                    )
                )
            ).one()[0] or 0

            # Cache the balance only for 5 seconds : it helps when listing
            # multiple categories by reducing sql requests
            cache.set('categorybalance-{0}'.format(self.id), balance, 5)

        for child in self.children:
            child_balance = child.balance(username)
            rate = helpers.rate(username,
                              child_balance['currency'], self.currency.isocode)
            balance['year'] = balance['year'] + child_balance['year'] * rate
            balance['month'] = balance['month'] + child_balance['month'] * rate
            balance['week'] = balance['week'] + child_balance['week'] * rate
            balance['7days'] = balance['7days'] + child_balance['7days'] * rate
            balance['30days'] = balance['30days'] +child_balance['30days']*rate

        return balance

    def all_parents_ids(self):
        parents = []
        if self.parent_id:
            parents.append(self.parent_id)
            parents = parents + self.parent.all_parents_ids()
        return parents

    def contains_category(self, categoryid):
        if self.id == categoryid:
            return True
        if self.children:
            for c in self.children:
                if c.contains_category(categoryid):
                    return True
        return False

    def as_dict(self, username, parent=True, children=True, balance=True):
        desc = {
            'id': self.id,
            'name': self.name,
            'currency': self.currency.isocode,
        }
        if balance:
            desc.update(self.balance(username))
        if parent and self.parent_id:
            desc['parent'] = self.parent_id
        if children and self.children:
            desc['children'] = [c.as_dict(username, False) \
                                                        for c in self.children]
        return desc



class Transaction(db.Model):
    id                   = db.Column(db.Integer, primary_key=True)
    owner_username       = db.Column(db.ForeignKey('user.username',
                                                   onupdate='CASCADE',
                                                   ondelete='CASCADE'),
                                     nullable=False)
    description          = db.Column(db.String(200), nullable=False)
    original_description = db.Column(db.String(200), nullable=False)
    amount               = db.Column(db.Numeric(15, 3), nullable=False)
    currency_id          = db.Column(db.ForeignKey('currency.id',
                                                   ondelete='CASCADE'),
                                     nullable=False)
    date                 = db.Column(db.Date, nullable=False)

    currency = db.relationship('Currency')

    def as_dict(self, username):
        return {
            'id': self.id,
            'description': self.description,
            'original_description': self.original_description,
            'amount': self.amount,
            'currency': self.currency.isocode,
            'date': self.date.strftime('%Y-%m-%d'),
            'accounts': [ta.as_dict(username) \
                                          for ta in self.transaction_accounts],
            'categories': [tc.as_dict(username) \
                                         for tc in self.transaction_categories]
        }



class TransactionAccount(db.Model):
    transaction_id = db.Column(db.ForeignKey('transaction.id',
                                             ondelete='CASCADE'),
                               primary_key=True)
    account_id     = db.Column(db.ForeignKey('account.id', ondelete='CASCADE'),
                               primary_key=True)
    amount         = db.Column(db.Numeric(15, 3), nullable=False)
    verified       = db.Column(db.Boolean, nullable=False, default=False)

    account = db.relationship('Account')
    transaction = db.relationship('Transaction', backref=db.backref(
                                                  'transaction_accounts',
                                                   cascade="all, delete-orphan"
                                                 ))

    def as_dict(self, username):
        data = self.account.as_dict(username, short=True)
        data['amount'] = self.amount
        data['verified'] = self.verified
        return data

    def as_tuple(self):
        return (self.account_id, self.amount)



class TransactionCategory(db.Model):
    transaction_id     = db.Column(db.ForeignKey('transaction.id',
                                                 ondelete='CASCADE'),
                                   primary_key=True)
    category_id        = db.Column(db.ForeignKey('category.id',
                                                 ondelete='CASCADE'),
                                   primary_key=True)
    transaction_amount = db.Column(db.Numeric(15, 3), nullable=False)
    category_amount    = db.Column(db.Numeric(15, 3), nullable=False)

    category = db.relationship('Category')
    transaction = db.relationship('Transaction', backref=db.backref(
                                                   'transaction_categories',
                                                   cascade="all, delete-orphan"
                                                 ))

    def as_dict(self, username):
        data = self.category.as_dict(username, parent=False,
                                     children=False,balance=False)
        data['transaction_amount'] = self.transaction_amount
        data['category_amount'] = self.category_amount
        return data

    def as_tuple(self):
        return (
            self.category_id,
            {
                'transaction_amount': self.transaction_amount,
                'category_amount': self.category_amount
            }
        )
