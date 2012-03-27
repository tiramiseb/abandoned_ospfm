#!/bin/sh

if [ "$1" = "clean" ]
then
    echo "Cleaning HTML documentation..."
    find . -name "*.rst" | while read file
    do
        rm -f "$(echo $file | sed 's/.rst$/.html/')"
    done
else

    RST2HTML=`which rst2html`

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
      $RST2HTML "$file" "$(echo $file | sed 's/.rst$/.html/')"
    done

    echo "All \".rst\" file have been converted to HTML."

fi
