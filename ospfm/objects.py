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

from flask import abort, jsonify, request

from ospfm import helpers


class Object:
    """
    When working with objects...

    ... an argument should be given to the "search", "read", "update" and
    "delete" methods. This argument may differ according to the object, but
    generally, "search" needs a search filter and the other ones need an
    identifier

    ... self.username should be set to the username of the current user or None

    ... self.args should be set to the args, especially for the "create" and
    "update" methods
    """

    def __init__(self, **kwargs):
        self.args = kwargs

    def __init_http(self):
        self.username = helpers.flask_get_username()
        if not self.username:
            abort(401)
        self.args = request.values

    def http_request(self, arg=None):
        """Deal with all HTTP requests"""
        # Prepare the environment
        self.__init_http()

        # Execute the request
        if request.method == 'GET' and not arg:
            response = self.list()
        elif request.method == 'GET' and arg:
            response = self.read(arg)
        elif request.method == 'POST':
            response = self.create()
        elif request.method == 'PUT':
            response = self.update(arg)
        elif request.method == 'DELETE':
            self.delete(arg)
            response = 'OK Deleted'
        # JSON response
        return jsonify(status=200, response=response)

    def list(self):
        """Override this method for objects listing"""
        raise NotImplementedError

    def create(self):
        """Override this method for object creation"""
        raise NotImplementedError

    def read(self, arg):
        """Override this method for object reading"""
        raise NotImplementedError

    def update(self, arg):
        """Override this method for object update"""
        raise NotImplementedError

    def delete(self, arg):
        """Override this method for object deletion"""
        raise NotImplementedError

    def search(self):
        """Override this method for object search"""
        raise NotImplementedError

    def badrequest(self):
        """Call this message to return a "bad request" response"""
        abort(400)

    def forbidden(self):
        """Call this message to return a "forbidden" response"""
        abort(403)

    def notfound(self):
        """Call this message to return a "not found" response"""
        abort(404)
