import webhelpers.feedgenerator as feedgenerator
from bs4 import BeautifulSoup
import urllib
import json
import sys
import tweepy
import random
import ConfigParser

def tweet(paper, credPath):
  with open(credPath) as data_file:
    cred = json.load(data_file)
  consumer_key = cred['cons_key']
  consumer_secret = cred['cons_sec']
  access_token = cred['acc_tok']
  access_token_secret = cred['acc_tok_sec']
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)
  # Construct message
  cheers = ["Yay", "Wow", "Woo", "Yes", "Aha", "Ooh", "OMG", "Joy", "Gee"]
  prefix = random.choice(cheers)
  prefix = prefix + "! A new secure computation paper on eprint, \""
  suffix = "\" https://ia.cr/" + paper['id']
  maxLength = 280 - len((prefix + suffix))
  title = " ".join((paper['title']).split())
  if len(title) > maxLength:
    title = title[:(maxLength - 3)] + "..."
  m = prefix + title + suffix
  api.update_status(m)
  print("tweeted:" + m)

def user_accept():
  yes = set(['yes','y','ye', ''])
  no = set(['no','n'])
  choice = raw_input().lower()
  if choice in yes:
    return True
  elif choice in no:
    return False
  else:
    sys.stdout.write("Please respond with 'yes' or 'no'")
    user_accept()

def make_feed(papers):
  feed = feedgenerator.Rss201rev2Feed(title=u"List of Secure Computation Papers",link=u"https://guutboy.github.io",description=u"A list of papers on IACR eprint on the topic of secure computation.",language=u"en")
  for p in papers[:50]:
    feed.add_item(title=p['title'], link=("https://eprint.iacr.org/" + p['id']), description=p['authors'], uniqueid=p['id'])
  return feed

if len(sys.argv) == 2 :
  eprintId = str(sys.argv[1]).split('/')
  if (len(eprintId) != 2):
    sys.exit('Malformed id: ' + str(sys.argv[1]))
  year = int(eprintId[0])
  serial = int(eprintId[1])
  ## Read path to unlabelled papers from config
  config = ConfigParser.RawConfigParser()
  config.read('config.cfg')
  papersPath = config.get('Web', 'web') + '/scripts/papers.json'
  rssPath = config.get('Web', 'web') + '/rss/list.rss'
  credPath = config.get('Web', 'cred')
  labelledPath = config.get('Data', 'labelled')
  with open(labelledPath) as labelled_file:
    labelled_papers = json.load(labelled_file)
  found = [p for p in labelled_papers if p['year'] == year and p['serial'] == serial]
  if (len(found) < 1):
    sys.exit('Could not find ' + str(sys.argv[1]))
  if (len(found) > 1):
    sys.exit('Found mutiple matches for ' + str(sys.argv[1]))
  foundPaper = found[0]
  paper = {
    'id':str(foundPaper['year']) + '/' + str(foundPaper['serial']).zfill(3),
    'title':foundPaper['title'],
    'authors':' and '.join(foundPaper['authors'])}
  # Load papers database
  with open(papersPath) as data_file:
    papers = json.load(data_file)
  # Check for duplicates
  matches = [p for p in papers if p['id'] == paper['id']]
  if len(matches) > 0 :
    sys.exit('paper with id ' + paper['id'] + ' is a duplicate link. Nothing added.')
  # Ask if paper should be added. If so we
  # 1) Write the updated database
  # 2) Write database to rss file
  # 3) Tweet about the added paper
  print(paper)
  sys.stdout.write('Would you like to add this paper? [Y/n]')
  sys.stdout.flush()
  if (user_accept()):
    papers.insert(0,paper)
    with open(papersPath, 'w') as data_file:
      json.dump(papers, data_file, separators=(',', ':'), indent=0, sort_keys=True)
    with open(rssPath, 'w') as rss_file:
      feed = make_feed(papers)
      feed.write(rss_file, 'utf-8')
    tweet(paper, credPath)
  else:
    sys.exit('No paper added.')
else:
  sys.exit('Not the right amount of arguments.');
