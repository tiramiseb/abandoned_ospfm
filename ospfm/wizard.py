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

import codecs
import datetime
import os

import ConfigParser

from flask import abort, jsonify, request

from sqlalchemy.exc import StatementError

from ospfm import app, authentication, config, db, helpers

from ospfm.core import models as core
from ospfm.transaction import models as transaction



@app.route('/wizard/<wizard>/<locale>/<currency>')
def wizards(wizard, locale, currency):
    try:
        username = authentication.get_username_auth(
                                     request.values.to_dict().get('key', None))
        if username in config.DEMO_ACCOUNTS:
            abort(400)
        delete_everything(username)
        status, response = create(username, wizard, locale, currency)
        return jsonify(status=status, response=response)
    except StatementError:
        db.session.rollback()


def delete_everything(username):
    """Delete all data except user preferences"""
    # Transaction
    #  -> TransactionAccount and TransactionCategory deleted by cascade
    transaction.Transaction.query.filter(
        transaction.Transaction.owner_username == username
    ).delete()
    # Category
    transaction.Category.query.filter(
        transaction.Category.owner_username == username
    ).delete()
    # Account
    # ... first get all accounts for the user...
    accountowners = transaction.AccountOwner.query.filter(
                        transaction.AccountOwner.owner_username == username
                    ).all()
    # ... then delete all "AccountOwner" links for the user...
    transaction.AccountOwner.query.filter(
        transaction.AccountOwner.owner_username == username
    ).delete()
    # ... and delete only accounts which do not have user associated...
    deleteaccounts = []
    for accountowner in accountowners:
        if not transaction.AccountOwner.query.filter(
                transaction.AccountOwner.account_id == accountowner.account_id
        ).first():
            deleteaccounts.append(
                transaction.Account.id == accountowner.account_id
            )
    if deleteaccounts:
        transaction.Account.query.filter(
            db.or_(*deleteaccounts)
        ).delete()
    # Currency
    core.Currency.query.filter(
        core.Currency.owner_username == username
    ).delete()
    # XXX TransactionAccounts are not deleted : problem with SQLite
    # Commit deletes
    db.session.commit()



def create(username, wizard, locale, prefcurrency):
    """Create entries from wizard files"""

    # /!\ Does not work in Python < 2.7
    #
    # (sections order is important)

    ########## Initialization
    data = ConfigParser.RawConfigParser()
    if wizard in ('basic', 'demo'):
        try:
            datafile = codecs.open(
                            os.path.join(config.WIZARD_DATA,'%s.basic'%locale),
                            'r', 'utf8'
                        )
            data.readfp(datafile)
            datafile.close()
        except:
            abort(400)
    if wizard == 'demo':
        try:
            datafile = codecs.open(
                            os.path.join(config.WIZARD_DATA, '%s.demo'%locale),
                            'r', 'utf8'
                        )
            data.readfp(datafile)
            datafile.close()
        except:
            abort(400)
    sections = data.sections()
    if not sections:
        return 200, 'OK'
    try:
        preferred_currency = core.Currency.query.filter(
                                    db.and_(
                                        core.Currency.isocode == prefcurrency,
                                        core.Currency.owner_username == None
                                    )
                                ).one()
    except:
        abort(400)

    today = datetime.date.today()

    ########## Helper functions
    def subsections(name):
        return [ i for i in sections if i.startswith(name) ]

    ########## Currency
    currencies = { prefcurrency: preferred_currency }
    for cur in subsections('currency-'):
        symbol = data.get(cur, 'symbol')
        currency = core.Currency(
                        owner_username = username,
                        isocode = symbol,
                        symbol = symbol,
                        name = data.get(cur, 'name'),
                        rate = data.get(cur, 'rate')
                    )
        db.session.add(currency)
        currencies[symbol] = currency
    db.session.commit()

    ########## Account
    accounts = {}
    for acc in subsections('account-'):
        if data.has_option(acc, 'currency'):
            curname = data.get(acc, 'currency')
            if curname not in currencies:
                currencies[curname] = core.Currency.query.filter(
                    db.and_(
                        core.Currency.owner_username == None,
                        core.Currency.isocode == curname
                    )
                ).one()
        else:
            curname = prefcurrency
        account = transaction.Account(
            name = data.get(acc, 'name'),
            currency = currencies[curname],
            start_balance = data.get(acc, 'balance')
        )
        db.session.add(account)
        accounts[acc.split('-')[1]] = account
        db.session.add(
            transaction.AccountOwner(
                account = account,
                owner_username = username
            )
        )
    db.session.commit()

    ########## Category
    categories = {}
    for cat in subsections('category-'):
        if data.has_option(cat, 'currency'):
            curname = data.get(cat, 'currency')
            if curname not in currencies:
                currencies[curname] = core.Currency.query.filter(
                    db.and_(
                        core.Currency.owner_username == None,
                        core.Currency.isocode == curname
                    )
                ).one()
        else:
            curname = prefcurrency
        category = transaction.Category(
            owner_username = username,
            currency = currencies[curname],
            name = data.get(cat, 'name')
        )
        try:
            category.parent = categories[data.get(cat, 'parent')]
        except:
            pass
        db.session.add(category)
        categories[cat.split('-')[1]] = category
    db.session.commit()

    ########## Transaction
    for tra in subsections('transaction-'):
        if data.has_option(tra, 'currency'):
            curname = data.get(tra, 'currency')
            if curname not in currencies:
                currencies[curname] = core.Currency.query.filter(
                    db.and_(
                        core.Currency.owner_username == None,
                        core.Currency.isocode == curname
                    )
                ).one()
        else:
            curname = prefcurrency
        currency = currencies[curname]
        # Calculate date
        year, month, day = data.get(tra, 'date').split('/')
        # Month
        if month:
            if month[0] in ('-', '+'):
                month = today.month + int(month)
            else:
                month = int(month)
        else:
            month = today.month
        # Year
        if year:
            if year[0] in ('-', '+'):
                year = today.year + int(year)
            elif year == '?':
                # If year = "?", point to the last passed year containing the
                # defined month (either current year or previous year)
                if month < today.month:
                    year = today.year
                else:
                    year = today.year - 1
            else:
                year = int(year)
        else:
            year = today.year
        # Check the month is not outside bounds, or correct the year
        def month_outside_bounds(month, year):
            if month < 1:
                month = month + 12
                year = year - 1
                month, year = month_outside_bounds(month, year)
            elif month > 12:
                month = month - 12
                year = year + 1
                month, year = month_outside_bounds(month, year)
            return month, year
        month, year = month_outside_bounds(month, year)
        # Day
        if day:
            if day[0] in ('-', '+'):
                daydeltafromfirst = today.day + int(day) - 1
                day = 1
            else:
                daydeltafromfirst = int(day) - 1
                day = 1
        else:
            day = today.day
            daydeltafromfirst = 0
        transactiondate = datetime.date(year,month,day)
        if daydeltafromfirst:
            transactiondate = transactiondate + \
                              datetime.timedelta(days=daydeltafromfirst)
        # Create transaction
        trans = transaction.Transaction(
            owner_username = username,
            description = data.get(tra, 'description'),
            amount = data.get(tra, 'amount'),
            currency = currency,
            date = transactiondate
        )
        try:
            trans.original_description = data.get(tra, 'original_description')
        except:
            trans.original_description = data.get(tra, 'description')
        db.session.add(trans)
        # Links to accounts
        for accountdata in data.get(tra, 'accounts').split():
            accountdatatb = accountdata.split(':')
            accountnum = accountdatatb[0]
            if len(accountdatatb) > 1:
                amount = accountdatatb[1]
            else:
                amount = trans.amount
            account = accounts[accountnum]
            accountamount = amount * helpers.rate(
                                            username,
                                            currency.isocode,
                                            account.currency.isocode
                                        )
            db.session.add(
                transaction.TransactionAccount(
                    transaction = trans,
                    account = account,
                    amount = accountamount
                )
            )
        # Links to categories
        for categorydata in data.get(tra, 'categories').split():
            categorydatatb = categorydata.split(':')
            categorynum = categorydatatb[0]
            if len(categorydatatb) > 1:
                amount = categorydatatb[1]
            else:
                amount = trans.amount
            category = categories[categorynum]
            categoryamount = amount * helpers.rate(
                                            username,
                                            currency.isocode,
                                            category.currency.isocode
                                        )
            db.session.add(
                transaction.TransactionCategory(
                    transaction = trans,
                    category = category,
                    transaction_amount = amount,
                    category_amount = categoryamount
                )
            )
    db.session.commit()

    ########## OK, finished
    return 200, 'OK'
