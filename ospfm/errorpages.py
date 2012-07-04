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

from flask import jsonify

from ospfm import app

@app.errorhandler(400)
def error400(e):
    response = jsonify(status=400, response='Bad request')
    response.status_code = 400
    return response

@app.errorhandler(401)
def error401(e):
    response = jsonify(status=401, response='Unauthorized')
    response.status_code = 401
    return response

@app.errorhandler(403)
def error403(e):
    response = jsonify(status=403, response='Access forbidden')
    response.status_code = 403
    return response

@app.errorhandler(404)
def error404(e):
    response = jsonify(status=404, response='Resource not found')
    response.status_code = 404
    return response

@app.errorhandler(405)
def error405(e):
    response = jsonify(status=405, response='Method not allowed')
    response.status_code = 405
    return response