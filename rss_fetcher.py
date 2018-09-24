from bs4 import BeautifulSoup
import urllib
import json
import sys
import ConfigParser
''' This script checks the IACR eprint RSS (actually the Atom feed, because this is easier to parse)
feed to check for new papers and stores new papers as an unlabelled record.

The script has functionality to scrape the year, serial number, title, authors list, abstract and
 keywords from the feed, which will then be stored as the unlabelled record for the paper. '''

def scrape_eprint_record(e):
  eprintId = e.id.string.replace('https://eprint.iacr.org/','')
  year = int(eprintId[:4])
  serial = int(eprintId[5:])
  title = e.title.string
  authors = [a.findAll('name')[0].string for a in e.findAll('author')]
  abstract = e.content.string
  keywords = [c['term'] for c in e.findAll('category')]
  record = {
    'year': year,
    'serial': serial,
    'title': title,
    'authors': authors,
    'abstract': abstract,
    'kw': keywords
  }
  return record

def is_newer_than(last_record, record):
  newer = record['year'] > last_record['year']
  newer = newer or (record['year'] == last_record['year'] 
                    and record['serial'] > last_record['serial'])
  return newer

## Read path to unlabelled papers from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
unlabelled_path =  config.get('Data', 'unlabelled')

## Fetch rss (atom) feed
url = urllib.urlopen('https://eprint.iacr.org/rss/atom.xml')
rss = url.read()
url.close()

## Read all entries
soup = BeautifulSoup(rss, 'xml')
entries = soup.findAll('entry')
## Read in unlabelled papers
with open(unlabelled_path, 'r') as json_file:
  records = json.load(json_file)
last_record = records[-1]
## Find any papers appearing in the rss feed not already stored as a unlabelled paper
new_records = []
for e in entries:
  r = scrape_eprint_record(e)
  if (is_newer_than(last_record, r)):
    new_records.append(r)

## Print the amout of new papers    
print str(len(new_records))
## If there are new papers add these to the file of unlabelled papers
if len(new_records) > 0:
  records = records + new_records
  records = sorted(records, key=lambda k: k['year'] * 10000 + k['serial'])
  with open(unlabelled_path, 'w') as json_file:
    json.dump(records, json_file, separators=(',', ':'), indent=0, sort_keys=True)

