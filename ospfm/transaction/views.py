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

from ospfm import app
from ospfm.transaction.account import Account
from ospfm.transaction.category import Category
from ospfm.transaction.transaction import Transaction

# ACCOUNTS

@app.route('/accounts', methods=['GET', 'POST'])
@app.route('/accounts/<accountid>', methods=['GET', 'POST', 'DELETE'])
def accounts(accountid=None):
    return Account().http_request(accountid)

# CATEGORIES
@app.route('/categories', methods=['GET', 'POST'])
@app.route('/categories/<categoryid>', methods=['GET', 'POST', 'DELETE'])
def categories(categoryid=None):
    return Category().http_request(categoryid)

# TRANSACTIONS
@app.route('/transactions', methods=['GET', 'POST'])
@app.route('/transactions/<transactionid>', methods=['GET', 'POST', 'DELETE'])
def transactions(transactionid=None):
    return Transaction().http_request(transactionid)

@app.route('/transactions/filter')
def transaction_filter():
    return Transaction().http_filter()
