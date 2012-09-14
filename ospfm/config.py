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

# Development options
DEVEL=True
SQLDEBUG=False
DEVEL_USERNAME='alice'

# Database URI
DATABASE='sqlite:////tmp/ospfm_devel.sqlite3'

# Cache system
from werkzeug.contrib.cache import SimpleCache
CACHE = SimpleCache()

LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 5001
