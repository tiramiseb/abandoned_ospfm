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

from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from ospfm import helpers
from ospfm.transaction import models
from ospfm.core import models as core

def accountbalance(username, accountid):
    account = models.Account.query.join(models.AccountOwner).filter(
                    and_(
                        models.AccountOwner.owner_username == username,
                        models.Account.id == accountid
                    )
              ).first()
    balances = account.balance(username)
    return {
        'id': accountid,
        'balance': balances[0],
        'balance_preferred': balances[1],
        'transactions_count': account.transactions_count()
    }

def totalbalance(username):
    accounts = models.Account.query.options(
                    joinedload(models.Account.currency)
    ).join(models.AccountOwner).filter(
        models.AccountOwner.owner_username == username
    ).all()
    # Calculate the total balance, in the user's preferred currency
    totalbalance = 0
    totalcurrency = core.User.query.options(
                        joinedload(core.User.preferred_currency)
                    ).get(username).preferred_currency
    for account in accounts:
        totalbalance += account.balance(username)[0] * \
        helpers.rate(username,
                     account.currency.isocode,
                     totalcurrency.isocode)
    return {
        'balance': totalbalance,
        'currency': totalcurrency.isocode
    }

def categoriesbalance(username, categoryid):
    category = models.Category.query.filter(
                    and_(
                        models.Category.owner_username == username,
                        models.Category.id == categoryid
                    )
              ).first()
    balances = category.balance(username)
    balances['id'] = categoryid
    result = [ balances ]
    # Also return parent category/ies balance(s)
    if category.parent_id:
        result.extend(categoriesbalance(username, category.parent_id))
    return result
