import webhelpers.feedgenerator as feedgenerator
from bs4 import BeautifulSoup
import urllib
import json
import sys
import tweepy
import random

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
  cheers = ["Yay", "Wow", "Woo", "Yes", "Aha", "Ooh", "Wee", "OMG"]
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

def scrape_from_eprint(eprintUrl):
  try:
    html_doc = urllib.urlopen(eprintUrl).read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    paper = {'id':soup.title.text[34:],'title':soup.b.text,'authors':soup.i.text}
    paper['title'] = " ".join((paper['title']).split())
    paper['authors'] = " ".join((paper['authors']).split())
  except:
    sys.exit("Error handling url \"" + url + "\". Please, check if it is correct.");
  return paper

if len(sys.argv) == 5 :
  eprintUrl = str(sys.argv[1])
  papersPath = str(sys.argv[2])
  rssPath = str(sys.argv[3])
  credPath = str(sys.argv[4])
  paper = scrape_from_eprint(eprintUrl)
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
