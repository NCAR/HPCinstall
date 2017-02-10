#!/bin/bash

# using ls to have things sorted alphabetically

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

stuff=""
for software in `ls --color=no -d $1`; do
    if [[ -d $software ]]; then
         more=$( for dir in $( ls --color=no $software ); do echo $dir; done | tail -1 )
         stuff="$stuff $software/$more"
    fi
done
tree -ifp $stuff  | grep '^\[-' | awk '{print $2}'
