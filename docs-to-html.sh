#!/bin/sh
#
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

if [ "$1" = "clean" ]
then
    echo "Cleaning HTML documentation..."
    find . -name "*.rst" | while read file
    do
        rm -f "$(echo $file | sed 's/.rst$/.html/')"
    done
else

    RST2HTML=`which rst2html`
    CSS="doc/ospfm.css"

    if [ -z "$RST2HTML" ]
    then
        echo "rst2html program not found." >&2
        echo "" >&2
        echo "Please install docutils or put rst2html in your PATH" >&2
        exit 1
    fi

    find . -name "*.rst" | while read file
    do
      echo "Converting $file"
      $RST2HTML --stylesheet $CSS "$file" "$(echo $file | sed 's/.rst$/.html/')"
    done

    echo "All \".rst\" file have been converted to HTML."

fi
