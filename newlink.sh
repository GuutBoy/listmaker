#!/bin/bash
MAIN_DIR=$(dirname $0)
WEB_KEY=web
CRED_KEY=cred

function look_up_config {
    echo $(grep ^$1[[:space:]]*= $MAIN_DIR/config.cfg | sed s/$1[[:space:]]*=[[:space:]]*//)
}

if [ ! -f $MAIN_DIR/config.cfg ]; then
    echo "No configuration file (config.cfg) found."
    exit 1
fi
WEB_DIR=$(look_up_config $WEB_KEY)
CRED=$(look_up_config $CRED_KEY)
JSON=$WEB_DIR/scripts/papers.json
RSS=$WEB_DIR/rss/list.rss

if [ "$#" -lt 1 ]; then
    echo "Error. Needs one or more arguments."
    exit 1
else
    # Get latest list of papers
    cd $WEB_DIR
    git pull
    # Update list of papers
    cd $MAIN_DIR
    UPDATE=false
    UPLOAD=false
    # Activate virtual env to use the python script
    source env/bin/activate
    # Add each new paper to the list (and tweet about them)
    for link in "$@"
    do
        python listmaker.py $link $JSON $RSS $CRED && UPDATE=true 
    done
    deactivate
    # Upload the list of papers if it was updated or if explicitly told to do so
    if $UPDATE; then
        UPLOAD=true
    else
        echo "No papers added. Do you wish to upload the list?"
        select yn in "Yes" "No"; do
            case $yn in
                Yes ) UPLOAD=true; break;;
                No ) exit 0;;
            esac
        done
    fi
    if $UPLOAD; then
        cd $WEB_DIR
        git add --all &&
        git commit -m "papers added" &&
        git push
    fi
    cd $MAIN_DIR
fi
exit 0
