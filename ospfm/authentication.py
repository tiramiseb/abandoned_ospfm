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

import bcrypt
import uuid

from flask import abort, jsonify, request

from ospfm import config
from ospfm.core import models as core

cache = config.CACHE

# First, authenticate the user with a username and password
# Next, authenticate API access with an API key, which is valid during 1 hour
# API keys are UUIDs v4. UUIDs v4 collision is very unlikely, so we may rely
# on it to identify a user temporarily.
# However, to be totally sure an access is legitimate, we also store the remote IP address locally...


# Keys are stored in cache. However, we should be careful here. It should
# work if the user interface stores the username and password and resend them
# on error 401 automatically.
#
# However, if a user interface does not store username and password, if
# anything happens with the cache (too much memory used, memcached restart,
# etc), users (maybe ALL users) will be disconnected.
#
# OSPFM-web temporarily stores username and password, so this is not a problem
# with it.
#
# Moving to a database storage is not excluded.

def authenticate(username=None, password=None, http_abort=True):
    if not username:
        username = request.values['username']
    if not password:
        password = request.values['password']

    user = core.User.query.filter(
                core.User.username == username
            ).first()
    if not user:
        if http_abort:
            abort(401)
        else:
            return False
    hashed = user.passhash
    if bcrypt.hashpw(password, hashed) == hashed:
        key = str(uuid.uuid4())
        cache.set(request.remote_addr+'---'+key, username, 3600)
        return jsonify(status=200, response={'key': key})
    elif http_abort:
        abort(401)
    else:
        return False

def get_username_auth(key):
        if key:
            username = cache.get(request.remote_addr+'---'+key)
            if username:
                return username
        if config.DEVEL and config.DEVEL_USERNAME:
            return config.DEVEL_USERNAME
        abort(401)
