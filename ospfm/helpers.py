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

import datetime

from flask import request

from ospfm import config

def flask_get_username():
    # remote_user contains the user's username when (s)he is authorized by the server
    if request.remote_user:
        return request.remote_user
    if config.DEVEL:
        return config.DEVEL_USERNAME
    return None

def date_from_string(string):
    # Convert a "YYYY-MM-DD" string to a date
    if len(string) == 10:
        try:
            return datetime.date(
                        int(string[:4]),
                        int(string[5:7]),
                        int(string[8:])
            )
        except:
            pass
    return None
