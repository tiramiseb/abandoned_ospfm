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

from ospfm import app, authentication, config

if config.DEVEL:
    @app.after_request
    def access_control_allow(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
        return response

@app.route('/')
def root():
    return 'This is an OSPFM server. More documentation will come later.'

@app.route('/login', methods=['POST'])
def login():
    return authentication.authenticate()

from ospfm.core import views
from ospfm.transaction import views
import wizard
