import json
import sys
import ConfigParser
''' This script prints the difference between the number of labelled papers and the number of
unlabelled papers. '''
def fullId(paper):
  id = paper['year'] + 10000 * paper['serial']

## Read path to unlabelled papers from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
unlabelled_path =  config.get('Data', 'unlabelled')
labelled_path =  config.get('Data', 'labelled')

with open(unlabelled_path, 'r') as json_file:
  records = json.load(json_file)

with open(labelled_path, 'r') as json_file:
  labelled_papers = json.load(json_file)

print len(records) - len(labelled_papers)
