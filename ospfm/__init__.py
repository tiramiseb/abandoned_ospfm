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

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from ospfm import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE
db = SQLAlchemy(app)

# App routing, etc
import ospfm.errorpages
import ospfm.views

from ospfm.transaction import additional as add_transaction

additional_methods = {}
for function in dir(add_transaction):
    if not function.startswith('__'):
        additional_methods[function] = getattr(add_transaction, function)
