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

def constructDataset(papers):
  mpc_examples = [p for p in papers if p['mpc']]
  train_size = len(mpc_examples) - (len(mpc_examples) / 5);
  shuffled_mpc = shuffle(mpc_examples, random_state=20)
  train_mpc = shuffled_mpc[:train_size]
  non_mpc_examples = [p for p in papers if not p['mpc']]
  shuffled_non_mpc = shuffle(non_mpc_examples, random_state=20)
  train_non_mpc = shuffled_non_mpc[:train_size]
  test_mpc = shuffled_mpc[train_size:]
  test_non_mpc = shuffled_non_mpc[train_size:]
  targets_mpc = [1] * train_size
  targets_non_mpc = [0] * train_size
  train = train_mpc + train_non_mpc
  targets = targets_mpc + targets_non_mpc
  train, targets = shuffle(train, targets, random_state=20)
  return { 
    'train_set' : train,
    'train_targets' : targets,
    'test_set' : test_non_mpc + test_mpc,
    'test_targets' : [0] * len(test_non_mpc) + [1] * len(test_mpc),
    'target_names' : ['non-mpc', 'mpc']
  }

def extract_attribute_dict(dataDict, attribute, join=False):
  if not join:
    return { 
      'train_set' : [p[attribute] for p in dataDict['train_set']],
      'train_targets' : dataDict['train_targets'],
      'test_set' : [p[attribute] for p in dataDict['test_set']],
      'test_targets' : dataDict['test_targets'],
      'target_names' : dataDict['target_names']
    }
  else:
    return { 
      'train_set' : [" ".join(p[attribute]) for p in dataDict['train_set']],
      'train_targets' : dataDict['train_targets'],
      'test_set' : [" ".join(p[attribute]) for p in dataDict['test_set']],
      'test_targets' : dataDict['test_targets'],
      'target_names' : dataDict['target_names']
    }
  

def train(dataDict, params):
  # build pipeline and train classifier
  text_clf = Pipeline([('vectorizer', CountVectorizer(ngram_range=params['ngram_range'], stop_words={'english'})), 
                       ('transformer', TfidfTransformer(use_idf=params['use_idf'])), 
                       ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=params['alpha'], max_iter=20, tol=None, n_jobs=-1)),])
  text_clf.fit(dataDict['train_set'], dataDict['train_targets'])
  # evaluate classifier
  predicted = text_clf.predict(dataDict['test_set'])
  met = metrics.classification_report(dataDict['test_targets'], predicted, target_names=dataDict['target_names'])
  # print results
  print met  
  return text_clf

def trainNum(dataDict):
  # build pipeline and train classifier
  clf = SGDClassifier(loss='hinge', penalty='l2', alpha=1e-4, max_iter=20, tol=None, n_jobs=-1)
  clf.fit(dataDict['train_set'], dataDict['train_targets'])
  # evaluate classifier
  predicted = clf.predict(dataDict['test_set'])
  met = metrics.classification_report(dataDict['test_targets'], predicted, target_names=dataDict['target_names'])
  # print results
  print met
  return clf

## Read path to unlabelled papers from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
labelled_path =  config.get('Data', 'labelled')
model_path =  config.get('Model', 'model')
# set up data 
with open(labelled_path) as dataFile:
  papers = json.load(dataFile)

dataDict = constructDataset(papers)
print 'Abstract'
abs_params = { 'ngram_range' : (1,2), 'alpha' : 0.0001, 'use_idf' : True }
abs_clf = train(extract_attribute_dict(dataDict, 'abstract'), abs_params)

print 'Title'
tit_params = { 'ngram_range' : (1,2), 'alpha' : 0.001, 'use_idf' : True }
tit_clf = train(extract_attribute_dict(dataDict, 'title'), tit_params)

print 'Key Words'
kw_params = { 'ngram_range' : (1,3), 'alpha' : 0.001, 'use_idf' : True }
kw_clf = train(extract_attribute_dict(dataDict, 'kw', join=True), kw_params)

print 'Authors'
aut_params = { 'ngram_range' : (1,4), 'alpha' : 1e-05, 'use_idf' : True }
aut_clf = train(extract_attribute_dict(dataDict, 'authors', join=True), aut_params)

tit_predictions = tit_clf.predict([p['title'] for p in papers]);
kw_predictions = kw_clf.predict([" ".join(p['kw']) for p in papers]);
abs_predictions = abs_clf.predict([p['abstract'] for p in papers]);
aut_predictions = aut_clf.predict([" ".join(p['authors']) for p in papers]);
for i in range(0, len(papers)):
  papers[i]['combi'] = [float(abs_predictions[i]), float(tit_predictions[i]), float(kw_predictions[i]), float(aut_predictions[i])]
combi_clf = trainNum(extract_attribute_dict(dataDict, 'combi'))
joblib.dump(abs_clf, model_path + "abs")
joblib.dump(tit_clf, model_path + "tit")
joblib.dump(kw_clf, model_path + "kw")
joblib.dump(aut_clf, model_path + "aut")
joblib.dump(combi_clf, model_path + "combi")

