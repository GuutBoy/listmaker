#!/bin/sh
#######
#
# Script to update the list of unlabelled paper from RSS feed, do predictions and make a 
# notification that there are new papers to be labelled. This is meant to be run periodically
#
#######
MAIN_DIR=$(dirname $0)
cd $MAIN_DIR
source env/bin/activate
NUM_NEW_PAPERS=$(python rss_fetcher.py)
NUM_MPC_PREDICTIONS=0
if [ ! $NUM_NEW_PAPERS -eq 0 ];then
    NUM_MPC_PREDICTIONS=$(python predictor.py)
fi
NUM_UNLABELLED=$(python unlabelled.py)
deactivate
if [ ! $NUM_UNLABELLED -eq 0 ]; then
    MESSAGE="New eprint papers $NUM_UNLABELLED, mpc predictions $NUM_MPC_PREDICTIONS"
    osascript -e "display notification \"$MESSAGE\" with title \"Eprint Update\""
fi
