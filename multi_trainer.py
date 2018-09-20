from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
from sklearn.utils import shuffle
from sklearn import metrics
import random 
import json
import ConfigParser
'''Trains a classifier to predict mpc papers.

This script loads the list of labelled eprint papers and trains a classifier on the abstracts of
each paper to tell the difference between non-mpc and mpc papers. The resulting model is written to
a file which can be loaded to do predictions of new papers.'''

def constructDataset(papers, attribute='abstract', list_att=False):
  if not list_att:
    mpc_examples = [p[attribute] for p in papers if p['mpc']]
  else:
    mpc_examples = [" ".join(p[attribute]) for p in papers if p['mpc']]
  train_size = len(mpc_examples) - (len(mpc_examples) / 10);
  shuffled_mpc = shuffle(mpc_examples)
  train_mpc = shuffled_mpc[:train_size]
  if not list_att:
    non_mpc_examples = [p[attribute] for p in papers if not p['mpc']]
  else:
    non_mpc_examples = [" ".join(p[attribute]) for p in papers if not p['mpc']]
  shuffled_non_mpc = shuffle(non_mpc_examples)
  train_non_mpc = shuffled_non_mpc[:train_size]
  test_mpc = shuffled_mpc[train_size:]
  test_non_mpc = shuffled_non_mpc[train_size:]
  targets_mpc = [1] * train_size
  targets_non_mpc = [0] * train_size
  train = train_mpc + train_non_mpc
  targets = targets_mpc + targets_non_mpc
  train, targets = shuffle(train, targets)
  return { 
    'train_set' : train,
    'train_targets' : targets,
    'test_set' : test_non_mpc + test_mpc,
    'test_targets' : [0] * len(test_non_mpc) + [1] * len(test_mpc),
    'target_names' : ['non-mpc', 'mpc']
  }

def train(dataDict, params):
  # build pipeline and train classifier
  text_clf = Pipeline([('vectorizer', CountVectorizer(ngram_range=params['ngram_range'], stop_words={'english'})), 
                       ('transformer', TfidfTransformer(use_idf=params['use_idf'])), 
                       ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=params['alpha'], max_iter=20, tol=None)),])
  text_clf.fit(dataDict['train_set'], dataDict['train_targets'])
  # evaluate classifier
  predicted = text_clf.predict(dataDict['test_set'])
  met = metrics.classification_report(dataDict['test_targets'], predicted, target_names=dataDict['target_names'])
  # print results
  print met  
  return text_clf

def trainNum(dataDict):
  # build pipeline and train classifier
  text_clf = Pipeline([('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-4, max_iter=20, tol=None)),])
  text_clf.fit(dataDict['train_set'], dataDict['train_targets'])
  # evaluate classifier
  predicted = text_clf.predict(dataDict['test_set'])
  met = metrics.classification_report(dataDict['test_targets'], predicted, target_names=dataDict['target_names'])
  # print results
  print met
  return text_clf

## Read path to unlabelled papers from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
labelled_path =  config.get('Data', 'labelled')
model_path =  config.get('Model', 'model')
# set up data 
with open(labelled_path) as dataFile:
  papers = json.load(dataFile)

print 'Abstract'
dataDict = constructDataset(papers)
abs_params = { 'ngram_range' : (1,2), 'alpha' : 0.0001, 'use_idf' : True }
abs_clf = train(dataDict, abs_params)

print 'Title'
dataDict = constructDataset(papers, 'title')
tit_params = { 'ngram_range' : (1,2), 'alpha' : 0.001, 'use_idf' : True }
tit_clf = train(dataDict, tit_params)

print 'Key Words'
dataDict = constructDataset(papers, 'kw', True)
kw_params = { 'ngram_range' : (1,3), 'alpha' : 0.001, 'use_idf' : True }
kw_clf = train(dataDict, kw_params)

print 'Authors'
dataDict = constructDataset(papers, 'authors', True)
aut_params = { 'ngram_range' : (1,4), 'alpha' : 1e-05, 'use_idf' : True }
aut_clf = train(dataDict, aut_params)

tit_predictions = tit_clf.predict([p['title'] for p in papers]);
kw_predictions = kw_clf.predict([" ".join(p['kw']) for p in papers]);
abs_predictions = abs_clf.predict([p['abstract'] for p in papers]);
aut_predictions = aut_clf.predict([" ".join(p['authors']) for p in papers]);
for i in range(0, len(papers)):
  papers[i]['combi'] = [float(abs_predictions[i]), float(tit_predictions[i]), float(kw_predictions[i]), float(aut_predictions[i])]
dataDict = constructDataset(papers, attribute='combi')
combi_clf = trainNum(dataDict)
joblib.dump(abs_clf, model_path + "abs")
joblib.dump(tit_clf, model_path + "tit")
joblib.dump(kw_clf, model_path + "kw")
joblib.dump(aut_clf, model_path + "aut")
joblib.dump(combi_clf, model_path + "combi")








#model_path =  config.get('Model', 'model')
#joblib.dump(text_clf, model_path)
