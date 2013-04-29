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

from ospfm import app, helpers
from ospfm.core.currency import Currency
from ospfm.core.preference import Preference
from ospfm.core.user import User, UserContact


# CURRENCIES

@app.route('/currencies', methods=['GET', 'POST'])
@app.route('/currencies/<isocode>', methods=['GET', 'POST', 'DELETE'])
def currencies(isocode=None):
    return Currency().http_request(isocode)

@app.route('/currencies/<fromisocode>/rate/<toisocode>')
def currencies_rate(fromisocode, toisocode):
    return Currency().http_rate(fromisocode, toisocode)

# USERS

@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/<username>', methods=['GET', 'POST', 'DELETE'])
def users(username=None):
    return User().http_request(username)

@app.route('/users/search/<criterion>')
def users_search(criterion):
    return User().http_search(criterion)

# USERCONTACTS

@app.route('/contacts', methods=['GET', 'POST'])
@app.route('/contacts/<username>', methods=['GET', 'POST', 'DELETE'])
def contacts(username=None):
    return UserContact().http_request(username)

# USERPREFERENCES

@app.route('/preferences', methods=['GET', 'POST'])
@app.route('/preferences/<preferencename>', methods=['GET', 'POST', 'DELETE'])
def preferences(preferencename=None):
    return Preference().http_request(preferencename)
