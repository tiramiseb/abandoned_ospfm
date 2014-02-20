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

import uuid

from passlib.hash import sha512_crypt

from flask import abort, jsonify, request

from ospfm import config
from ospfm.core import models as core

cache = config.CACHE

# First, authenticate the user with a username and password
# Next, authenticate API access with an API key, which is valid during 1 hour
# API keys are UUIDs v4. UUIDs v4 collision is very unlikely, so we may rely
# on it to identify a user temporarily.
# However, to be totally sure an access is legitimate, we also store the remote IP address locally...


# Keys are stored in cache.
#
# If anything happens with the cache (too much memory used, memcached restart,
# etc), users will be disconnected.
#
# Moving to a database storage is not excluded.

def authenticate(username=None, password=None, http_abort=True):
    if not username:
        username = request.values['username']
    if not password:
        password = request.values['password']

    # Refuse the login if there has been 3 previous failed attempts
    fails = cache.get(request.remote_addr+'-'+username+'-authfails') or 0
    # Minimal protection against passwords guess attempts
    if fails > 2:
        cache.set(request.remote_addr+'-'+username+'-authfails', fails, 120)
        abort(401, '3 previous attempts failed, please wait 2 minutes')
        # The following line is there only for the translation in OSPFM-web
        # self.forbidden('3 previous attempts failed, please wait 2 minutes')

    user = core.User.query.filter(
                core.User.username == username
            ).first()
    if not user:
        if http_abort:
            cache.set(request.remote_addr+'-'+username+'-authfails',
                      fails+1, 120)
            abort(401, 'Wrong username or password')
            # The following line is there only for the translation in OSPFM-web
            # self.forbidden('Wrong username or password')
        else:
            return False
    if sha512_crypt.verify(password, user.passhash):
        # Last login was not a fail, remove the fail info in the cache
        cache.delete(request.remote_addr+'-'+username+'-authfails')
        key = str(uuid.uuid4())
        cache.set(request.remote_addr+'---'+key, username, 1800)
        return jsonify(status=200, response={'key': key})
    elif http_abort:
        # Minimal protection against passwords guess attempts: each login
        # failure increments this counter
        cache.set(request.remote_addr+'-'+username+'-authfails', fails+1, 120)
        abort(401, 'Wrong username or password')
    else:
        return False

def get_username_auth(key):
        if key:
            username = cache.get(request.remote_addr+'---'+key)
            if username:
                # Extend the key validity, 30 more minutes
                cache.set(request.remote_addr+'---'+key, username, 1800)
                return username
        if config.DEVEL and config.DEVEL_USERNAME:
            return config.DEVEL_USERNAME
        abort(401, 'Please login')
