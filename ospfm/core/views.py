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

from ospfm import app, http_helpers
from ospfm.core.currency import Currency
from ospfm.core.user import User, UserContact, UserEmail

# CURRENCIES

@app.route('/currencies', methods=['GET', 'POST'])
@app.route('/currencies/<symbol>', methods=['GET', 'PUT', 'DELETE'])
def currencies(symbol=None):
    return Currency().http_request(symbol)

@app.route('/currencies/<fromsymbol>/rate/<tosymbol>')
def currencies_rate(fromsymbol, tosymbol):
    return Currency().http_rate(fromsymbol, tosymbol)

# USERS

@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/<username>', methods=['GET', 'PUT', 'DELETE'])
def users(username=None):
    return User().http_request(username)

@app.route('/users/me', methods=['GET', 'PUT', 'DELETE'])
def users_me():
    return users(http_helpers.get_username())

@app.route('/users/search/<criteria>')
def users_search(criteria):
    return User().http_search(criteria)

# USERCONTACTS

@app.route('/contacts', methods=['GET', 'POST'])
@app.route('/contacts/<username>', methods=['GET', 'PUT', 'DELETE'])
def contacts(username=None):
    return UserContact().http_request(username)

# USEREMAILS

@app.route('/emails', methods=['GET', 'POST'])
@app.route('/emails/<email_address>', methods=['GET', 'PUT', 'DELETE'])
def emails(email_address=None):
    return UserEmail().http_request(email_address)
