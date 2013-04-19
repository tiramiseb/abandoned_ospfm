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

from sqlalchemy import and_, Boolean, Column, Date, ForeignKey, func,\
                       Integer, Numeric, String
from sqlalchemy.orm import relationship, backref, joinedload
from sqlalchemy.schema import UniqueConstraint

from ospfm import config, helpers
from ospfm.core import exchangerate, models as coremodels
from ospfm.database import Base, session

cache = config.CACHE

class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    currency_id = Column(ForeignKey('currency.id', ondelete='CASCADE'))
    start_balance = Column(Numeric(15, 3), nullable=False)

    currency = relationship('Currency', backref=backref(
                                     'accounts', cascade='all, delete-orphan'))

    def balance(self, username):
        """
        Return a list :
            ( <balance in account currency>, <balance in preferred currency> )
        """
        balance = session.query(
            func.sum(TransactionAccount.amount)
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
                    joinedload(coremodels.User.preferred_currency)
                ).get(
                    username
                ).preferred_currency.isocode
            ) * balances[0]
        )
        return balances

    def transactions_count(self):
        return session.query(
            func.count(TransactionAccount.transaction_id)
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


class AccountOwner(Base):
    __tablename__ = 'accountowner'
    account_id = Column(ForeignKey('account.id', ondelete='CASCADE'),
                        primary_key=True)
    owner_username = Column(ForeignKey('user.username', ondelete='CASCADE'),
                            primary_key=True)

    account = relationship('Account', backref=backref(
                               'account_owners', cascade='all, delete-orphan'))
    owner = relationship('User', backref=backref(
                               'accounts_owner', cascade='all, delete-orphan'))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    owner_username = Column(ForeignKey('user.username', ondelete='CASCADE'),
                            nullable=False)
    parent_id = Column(ForeignKey('category.id', ondelete='SET NULL'))
    currency_id = Column(ForeignKey('currency.id', ondelete='CASCADE'))
    name = Column(String(50), nullable=False)

    owner = relationship('User', backref=backref(
                                   'categories', cascade='all, delete-orphan'))
    children = relationship('Category',
                            backref=backref('parent', remote_side=[id]),
                            order_by='Category.name')
    currency = relationship('Currency', backref=backref(
                                   'categories', cascade='all, delete-orphan'))

    def balance(self, username):
        today = datetime.date.today()

        balance = cache.get('categorybalance-{0}'.format(self.id))

        if not balance:

            balance = {'currency': self.currency.isocode};

            balance['year'] = session.query(
                func.sum(TransactionCategory.category_amount)
            ).filter(
                and_(
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
            balance['month'] = session.query(
                func.sum(TransactionCategory.category_amount)
            ).filter(
                and_(
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
            balance['week'] = session.query(
                func.sum(TransactionCategory.category_amount)
            ).filter(
                and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        firstdayofweek,
                        lastdayofweek
                    )
                )
            ).one()[0] or 0

            balance['7days'] = session.query(
                func.sum(TransactionCategory.category_amount)
            ).filter(
                and_(
                    TransactionCategory.category_id == self.id,
                    TransactionCategory.transaction_id == Transaction.id,
                    Transaction.date.between(
                        today - datetime.timedelta(6),
                        today
                    )
                )
            ).one()[0] or 0

            balance['30days'] = session.query(
                func.sum(TransactionCategory.category_amount)
            ).filter(
                and_(
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

    def contains_category(self, categoryid):
        if self.id == categoryid:
            return True
        if self.children:
            for c in self.children:
                if c.contains_category(categoryid):
                    return True
        return False


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    owner_username = Column(ForeignKey('user.username', ondelete='CASCADE'),
                            nullable=False)
    description = Column(String(200), nullable=False)
    original_description = Column(String(200), nullable=False)
    amount = Column(Numeric(15, 3), nullable=False)
    currency_id = Column(ForeignKey('currency.id', ondelete='CASCADE'),
                         nullable=False)
    date = Column(Date, nullable=False)

    owner = relationship('User', backref=
                          backref('transactions', cascade='all, delete-orphan'))
    currency = relationship('Currency', backref=
                          backref('transactions', cascade='all, delete-orphan'))


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


class TransactionAccount(Base):
    __tablename__ = 'transactionaccount'
    transaction_id = Column(ForeignKey('transaction.id', ondelete='CASCADE'),
                            primary_key=True)
    account_id = Column(ForeignKey('account.id', ondelete='CASCADE'),
                        primary_key=True)
    amount = Column(Numeric(15, 3), nullable=False)
    verified = Column(Boolean, nullable=False, default=False)

    transaction = relationship('Transaction', backref=backref(
                          'transaction_accounts', cascade='all, delete-orphan'))
    account = relationship('Account', backref=backref(
                          'transactions_account', cascade='all, delete-orphan'))

    def as_dict(self, username):
        data = self.account.as_dict(username, short=True)
        data['amount'] = self.amount
        data['verified'] = self.verified
        return data

    def as_tuple(self):
        return (self.account_id, self.amount)


class TransactionCategory(Base):
    __tablename__ = 'transactioncategory'
    transaction_id = Column(ForeignKey('transaction.id', ondelete='CASCADE'),
                            primary_key=True)
    category_id = Column(ForeignKey('category.id', ondelete='CASCADE'),
                         primary_key=True)
    transaction_amount = Column(Numeric(15, 3), nullable=False)
    category_amount = Column(Numeric(15, 3), nullable=False)

    transaction = relationship('Transaction', backref=backref(
                        'transaction_categories', cascade='all, delete-orphan'))
    category = relationship('Category', backref=backref(
                         'transactions_category', cascade='all, delete-orphan'))

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
