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

def constructDataset(papers, attribute='abstract'):
  random.seed(42)
  mpc_abs = [p[attribute] for p in papers if p['mpc']]
  train_size = len(mpc_abs) - (len(mpc_abs) / 10);
  train_mpc = random.sample(mpc_abs, train_size);
  non_mpc_abs = [p[attribute] for p in papers if not p['mpc']]
  train_non_mpc = random.sample(non_mpc_abs, train_size);
  test_mpc = [a for a in mpc_abs if not a in train_mpc]
  test_non_mpc = [a for a in non_mpc_abs if not a in train_non_mpc]
  targets_mpc = [1] * train_size
  targets_non_mpc = [0] * train_size
  train = train_mpc + train_non_mpc
  targets = targets_mpc + targets_non_mpc
  train, targets = shuffle(train, targets, random_state=42)
  return { 
    'train_set' : train,
    'train_targets' : targets,
    'test_set' : test_non_mpc + test_mpc,
    'test_targets' : [0] * len(test_non_mpc) + [1] * len(test_mpc),
    'target_names' : ['non-mpc', 'mpc']
  }


## Read path to unlabelled papers from config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
labelled_path =  config.get('Data', 'labelled')
model_path =  config.get('Model', 'model')

# set up data 
with open(labelled_path) as dataFile:
  papers = json.load(dataFile)
dataDict = constructDataset(papers)

# build pipeline and train classifier
text_clf = Pipeline([('vectorizer', CountVectorizer(ngram_range=(1, 2), stop_words={'english'})), 
                     ('transformer', TfidfTransformer()), 
                     ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-4, random_state=42, max_iter=20, tol=None)),])
text_clf.fit(dataDict['train_set'], dataDict['train_targets'])
# evaluate classifier
predicted = text_clf.predict(dataDict['test_set'])
met = metrics.classification_report(dataDict['test_targets'], predicted, target_names=dataDict['target_names'])
# print results
print met
# grid search stuff
#parameters = {'vectorizer__ngram_range': [(1, 2), (1, 3), (1, 4)], 'transformer__use_idf': (True, False), 'clf__alpha': (1e-3, 1e-4, 1e-5), }
#gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
#gs_clf = gs_clf.fit(dataDict['train_set'], dataDict['train_targets'])
#predicted = gs_clf.predict(dataDict['test_set'])
#met = metrics.classification_report(dataDict['test_targets'], predicted, target_names=dataDict['target_names'])
#print results
#print met
#print gs_clf.best_score_
#for param_name in sorted(parameters.keys()):
#  print("%s: %r" % (param_name, gs_clf.best_params_[param_name]))

joblib.dump(text_clf, model_path)
