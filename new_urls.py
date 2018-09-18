import json
import sys
import ConfigParser
''' This script prints a list of urls for papers that has been labelled mpc but is not yet listed as mpc papers.
'''
def eprintId(labelled_paper):
  return str(p['year']) + '/' + str(p['serial']).rjust(3, '0')

## Read path to labelled papers and the web dir from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
labelled_path =  config.get('Data', 'labelled')
web_path =  config.get('Web', 'web')

with open (labelled_path) as labelled_file:
  labelled_papers = json.load(labelled_file)

labelled_mpc_papers = [p for p in labelled_papers if p['mpc']]

with open (web_path + "/scripts/papers.json") as mpc_file:
  papers = json.load(mpc_file)

new_urls = [eprintId(p) for p in labelled_mpc_papers if( not any( q['id'] == eprintId(p) for q in papers))]

print " ".join(new_urls)
