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

########## App initialisation

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from ospfm import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE
db = SQLAlchemy(app)

########## App routing, etc

import ospfm.errorpages
import ospfm.views

########## Additional methods

from ospfm.transaction import additional as add_transaction
# ^ Add a line for each section

additional_methods = {}
for function in dir(add_transaction):
    if not function.startswith('__'):
        additional_methods[function] = getattr(add_transaction, function)

########## Database initialization

def init_db():
    """Create the database tables"""
    import ospfm.core.models
    import ospfm.transaction.models
    # ^ Add a line for each section
    db.create_all()
