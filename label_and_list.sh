#!/bin/bash
MAIN_DIR=$(dirname $0)
pushd $MAIN_DIR
source env/bin/activate
echo "Opening menu  ... "
python menu.py
deactivate
NEW_URLS=$(python new_urls.py)
if [ ! -z "$NEW_URLS" ]; then
    ./newlink.sh $NEW_URLS 
fi
popd
