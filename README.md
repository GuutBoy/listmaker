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
unlabelled = "PATH TO UNLABELLED PAPERS"
labelled = "PATH TO LABELLED PAPERS"
[Model]
model = "PATH TO TRAINED MODEL"
```
