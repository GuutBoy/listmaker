from sklearn.externals import joblib
import json
import sys
import ConfigParser
"""Adds mpc predictions to eprint papers.

This script loads the unlabelled eprint papers and finds all papers that does not have
an mpc prediction yet. It then loads a a pre-trained classifier and uses it
to add predictions to all papers found in the first step. The result is written back to
the file of unlabelled papers"""

def combi_predictions(unpredicted, model_path):
  abs_clf = joblib.load(model_path + "abs")
  tit_clf = joblib.load(model_path + "tit")
  kw_clf = joblib.load(model_path + "kw")
  aut_clf = joblib.load(model_path + "aut")
  combi_clf = joblib.load(model_path + "combi")
  tit_predictions = tit_clf.predict([p['title'] for p in unpredicted]);
  kw_predictions = kw_clf.predict([" ".join(p['kw']) for p in unpredicted]);
  abs_predictions = abs_clf.predict([p['abstract'] for p in unpredicted]);
  aut_predictions = aut_clf.predict([" ".join(p['authors']) for p in unpredicted]);
  combi_features = []
  for i in range(0, len(unpredicted)):
    feature = [float(abs_predictions[i]), float(tit_predictions[i]), float(kw_predictions[i]), float(aut_predictions[i])]
    combi_features.append(feature)
  return combi_clf.predict(combi_features)

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
  predicted = combi_predictions(unpredicted, model_path)
  for i in range(0, len(unpredicted)):
    paper = unpredicted[i]
    if predicted[i] == 1:
      mpc_count += 1
      paper[u'pred'] = True
    else:
      paper[u'pred'] = False
      
  with open(unlabelled_path, 'w') as dataFile:
    json.dump(papers, dataFile, separators=(',', ':'), indent=0, sort_keys=True)
print str(mpc_count)
