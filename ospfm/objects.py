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

from flask import abort, jsonify, request
from sqlalchemy.exc import StatementError

import ospfm
from ospfm import authentication, db

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
    emptyvalid = []

    def __init__(self, **kwargs):
        self.args = kwargs
        self.add_data = []
        # Empty values are forbidden if they are not in emptyvalid
        for item in self.args.items():
            if item[1] == '' and item[0] not in self.emptyvalid:
                self.badrequest()

    def __init_http(self):
        self.args = request.values.to_dict()
        self.username = authentication.get_username_auth(
                            self.args.get('key', None)
                        )

    def add_to_response(self, *args):
        """Adds an additional data to the response"""
        self.add_data.append(args)

    def http_request(self, arg=None):
        """Deal with all HTTP requests"""
        # Prepare the environment
        self.__init_http()
        try:
            # Execute the request
            if request.method == 'GET':
                if arg:
                    response = self.read(arg)
                else:
                    response = self.list()
            elif request.method == 'POST':
                if '_method' in self.args and self.args['_method'] == 'delete':
                    self.delete(arg)
                    response = 'OK Deleted'
                else:
                    if arg:
                        response = self.update(arg)
                    else:
                        response = self.create()
            elif request.method == 'DELETE':
                self.delete(arg)
                response = 'OK Deleted'
            # Create additional data
            additional_data = []
            for data in self.add_data:
                additional_data.append([
                    data[0],
                    ospfm.additional_methods[data[0]](self.username, *data[1:])
                ])
            # JSON response
            if additional_data:
                return jsonify(status=200, response=response,
                               additional=additional_data)
            else:
                return jsonify(status=200, response=response)
        except StatementError:
            db.session.rollback()
            self.badrequest()

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
