#!/bin/bash

# using ls to have things sorted alphabetically

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <directory>"
    echo "       where directory is e.g. ~/github/ys-install-scripts"
    exit 1
fi

stuff=""
for software in `ls --color=no $1`; do
    if [[ -d $software ]]; then
         more=$( for dir in $( ls --color=no $software ); do echo $dir; done | tail -1 )
         stuff="$stuff $software/$more"
    fi
done
tree -ifp $1/$stuff  | grep '^\[-' | awk '{print $2}'
