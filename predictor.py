from sklearn.externals import joblib
import json
import sys
import ConfigParser
"""Adds mpc predictions to eprint papers.

This script loads the unlabelled eprint papers and finds all papers that does not have
an mpc prediction yet. It then loads a a pre-trained classifier and uses it
to add predictions to all papers found in the first step. The result is written back to
the file of unlabelled papers"""

## Read path to unlabelled papers and model from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
unlabelled_path =  config.get('Data', 'unlabelled')
model_path =  config.get('Model', 'model')

with open(unlabelled_path) as dataFile:
  papers = json.load(dataFile)
unpredicted = [p for p in papers if 'pred' not in p]
mpc_count = 0
if len(unpredicted) > 0:
  clf = joblib.load(model_path)
  predicted = clf.predict([p['abstract'] for p in unpredicted])
  for i in range(0, len(unpredicted)):
    paper = unpredicted[i]
    if predicted[i] == 1:
      mpc_count += 1
      paper[u'pred'] = True
    else:
      paper[u'pred'] = False
      
  with open(unlabelled_path, 'w') as dataFile:
    json.dump(papers, dataFile)
print str(mpc_count)
