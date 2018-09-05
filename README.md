# Listmaker
Scripts to update guutboy.github.io

# Setup
To setup virtual environment run: 
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
deactivate
```
Write the file `config.cfg` containing the following 
```
[Web]
web = "PATH TO WEB STUFF"
cred = "PATH TO TWITTER STUFF"
[Data]
unlabelled = "PATH TO JSON FILE LISTING UNLABELLED PAPERS"
labelled = "PATH TO JSON FILE LISTING LABELLED PAPERS"
[Model]
model = "PATH TO TRAINED MODEL"
```

# Usage

The collection of scripts can be used to fetch the data on new papers from ePrint, run a simple
classifier to predict mpc papers, manually label papers as being mpc or not and to update the list
of mpc papers on the website and rss feed. There are two main scripts:

## Update List of Unlabelled Papers
To find new papers run the `update.sh` script. It will check the RSS feed for new papers, run the
predictor in order to attempt to predict whether papers are MPC or not, and then add the result the
json file listing unlabelled papers. On MacOS it will also give notification that there are new
papers on ePrint. This script can conveniently be run periodically in the background.

## Label New Papers and List on Website
To update the list with new papers run the `label_and_list.sh` script. It will start a simple text
UI that can be used to label new papers as MPC or non-MPC papers. When the UI is closed (pressing
`q`), it will write newly labelled papers to the json file listing the labelled papers. The script
will then ask if you want to add the papers to the list. If so a tweet will be made about the paper
and the paper will be added to the list of papers on the website.
