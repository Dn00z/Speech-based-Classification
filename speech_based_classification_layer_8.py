# -*- coding: utf-8 -*-
"""Speech-based Classification Layer-8.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KR-79CAu_ii4KPAJz8um-eV51b5sDvgr

# Importing Libraries
"""

import numpy as np
from sklearn import svm
from sklearn import metrics
from sklearn.model_selection import RandomizedSearchCV
from sklearn.feature_selection import SelectKBest
import matplotlib.pyplot as plt
import seaborn as sn
from sklearn.model_selection import cross_val_score

"""# Preprocessing Data

## Loading Data
"""

# from google.colab import drive
# drive.mount('/content/drive')

# import pandas as pd

# file_path = '/content/drive/MyDrive/ML-Project/dataset-01'

# train_df = pd.read_csv(f'{file_path}/train.csv')
# valid_df = pd.read_csv(f'{file_path}/valid.csv')

import pandas as pd

file_path = './dataset-01'

train_df = pd.read_csv(f'{file_path}/train.csv')
valid_df = pd.read_csv(f'{file_path}/valid.csv')
test_df = pd.read_csv(f'{file_path}/test.csv')

train_df.shape

L1 = 'label_1'
L2 = 'label_2'
L3 = 'label_3'
L4 = 'label_4'

labels = [L1, L2, L3, L4]
features = [f'feature_{i}' for i in range(1, 769)]

X_train = {}
y_train = {}

X_valid = {}
y_valid = {}


X_test = test_df.drop('ID', axis=1)
test_predicts = {}

"""## Scaling Data

"""

from sklearn.preprocessing import RobustScaler

for label in labels:
  tr_df = train_df[train_df[L2].notna()] if label == L2 else train_df
  val_df = valid_df[valid_df[L2].notna()] if label == L2 else valid_df

  scalar = RobustScaler()

  X_train[label] = pd.DataFrame(scalar.fit_transform(tr_df.drop(labels, axis=1)), columns=features)
  y_train[label] = tr_df[label]

  X_valid[label] = pd.DataFrame(scalar.transform(val_df.drop(labels, axis=1)), columns=features)
  y_valid[label] = val_df[label]

  pd.DataFrame(scalar.transform(X_test), columns=features)

"""# Main functions

## Classifier
"""

def svm_classifier(X_train, y_train, class_weight=None):
    clf = svm.SVC(class_weight=class_weight)
    clf.fit(X_train, y_train)
    return clf

"""## Get model performance"""

def printValidationPerformance(clf, X, y):

  y_pred = clf.predict(X)

  # print(metrics.confusion_matrix(y, y_pred))
  print('Accuracy: ', metrics.accuracy_score(y, y_pred))
  print('Precision: ', metrics.precision_score(y, y_pred, average='weighted'))
  print('F1 score: ', metrics.f1_score(y, y_pred, average='weighted'))

"""## Methods for hyperparameter tuning"""

def random_search(clf, param_grid, cv, n_iter, X_train, y_train):

    grid = RandomizedSearchCV(clf, param_grid, n_iter=n_iter, n_jobs=-1, cv=cv, verbose=1, scoring='accuracy')
    grid.fit(X_train, y_train)
    return grid

"""## Cross Validation"""

def cross_validation(clf, k, X_train, y_train):

    scores = cross_val_score(clf, X_train, y_train, cv=k)
    mean_score = np.mean(scores)
    std_dev = np.std(scores)
    print("Scores:", scores)
    print("Mean Score:", mean_score)
    print("Standard Deviation:", std_dev)

"""# Label 01

## Performance before Feature Engineering
"""

clf = svm_classifier(X_train[L1], y_train[L1])

"""### Training Performance"""

printValidationPerformance(clf, X_train[L1], y_train[L1])

"""### Validation Performance"""

printValidationPerformance(clf, X_valid[L1], y_valid[L1])

"""## Feature Engineering"""

plt.figure(figsize=(18, 6))
sn.countplot(data=y_train, x=L1)

"""### Feature selection - univariant feature selection"""

selector = SelectKBest(k=200)
X_train_skb = selector.fit_transform(X_train[L1], y_train[L1])

X_train_skb.shape

clf_1 = svm_classifier(X_train_skb, y_train[L1])

"""#### Training Accuracy"""

printValidationPerformance(clf_1, X_train_skb, y_train[L1])

"""#### Validataion Accuracy"""

printValidationPerformance(clf_1, selector.transform(X_valid[L1]), y_valid[L1])

"""### Feature selection - PCA"""

from sklearn.decomposition import PCA

selector_pca = PCA(n_components=0.95, svd_solver='full')
X_train_pca = pd.DataFrame(selector_pca.fit_transform(X_train[L1]))

X_train_pca.shape

clf_pca = svm_classifier(X_train_pca, y_train[L1])

"""#### Training Accuracy"""

printValidationPerformance(clf_pca, X_train_pca, y_train[L1])

"""#### Validation Accuracy"""

printValidationPerformance(clf_pca, selector_pca.transform(X_valid[L1]), y_valid[L1])

"""## Hyperparameter Tuning"""

clf = svm.SVC()

param_grid = {
    'C': np.logspace(-3, 3, 7),
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': np.logspace(-3, 3, 7)
    }

grid = random_search(clf, param_grid, cv=2, n_iter=5, X_train=X_train_pca, y_train=y_train[L1])

print('best parameters: ', grid.best_params_)

"""### Validation Accuracy"""

#best parameters:  {'kernel': 'rbf', 'gamma': 0.01, 'C': 10}

printValidationPerformance(grid.best_estimator_, selector_pca.transform(X_valid[L1]), y_valid[L1])

"""## Cross Validation"""

model = svm.SVC(kernel='rbf', gamma=0.01, C=10)
cross_validation(model, 5, X_train_skb, y_train[L1])

"""## Selected Parameters for L1"""

clf_L1 = svm.SVC(kernel='rbf', gamma=0.01, C=10)
clf_L1.fit(X_train_pca, y_train[L1])
X_test_L1 = selector.transform(X_test)

printValidationPerformance(clf_L1, selector_pca.transform(X_valid[L1]), y_valid[L1])

"""# Label 02

## Performance before Feature Engineering
"""

clf = svm_classifier(X_train[L2], y_train[L2])

"""### Training Performance"""

printValidationPerformance(clf, X_train[L2], y_train[L2])

"""### Validation Performance"""

printValidationPerformance(clf, X_valid[L2], y_valid[L2])

"""## Feature Engineering"""

plt.figure(figsize=(18, 6))
sn.countplot(data=y_train, x=L2)

"""### Feature selection - univariant feature selection"""

selector_L2 = SelectKBest(k=230)
X_train_skb_L2 = selector_L2.fit_transform(X_train[L2], y_train[L2])

X_train_skb_L2.shape

clf_2 = svm_classifier(X_train_skb_L2, y_train[L2])

"""#### Training Accuracy"""

printValidationPerformance(clf_2, X_train_skb_L2, y_train[L2])

"""#### Validataion Accuracy"""

printValidationPerformance(clf_2, selector_L2.transform(X_valid[L2]), y_valid[L2])

"""### Feature selection - PCA"""

from sklearn.decomposition import PCA

selector_pca_L2 = PCA(n_components=0.96, svd_solver='full')
X_train_pca_L2 = pd.DataFrame(selector_pca_L2.fit_transform(X_train[L2]))

X_train_pca_L2.shape

clf_pca_L2 = svm_classifier(X_train_pca_L2, y_train[L2])

"""#### Training Accuracy"""

printValidationPerformance(clf_pca_L2, X_train_pca_L2, y_train[L2])

"""#### Validation Accuracy"""

printValidationPerformance(clf_pca_L2, selector_pca_L2.transform(X_valid[L2]), y_valid[L2])

"""## Hyperparameter Tuning"""

clf_2 = svm.SVC()

param_grid = {
    'C': np.logspace(-3, 3, 7),
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': np.logspace(-3, 3, 7),
    'class_weight': ['balanced']
}

grid_2 = random_search(clf_2, param_grid, cv=2, n_iter=5, X_train=X_train_pca_L2, y_train=y_train[L2])

print('best parameters: ', grid_2.best_params_)

"""### Validation Accuracy"""

printValidationPerformance(grid_2.best_estimator_, selector_pca_L2.transform(X_valid[L2]), y_valid[L2])

"""## Cross Validation"""

model = svm.SVC(kernel='poly', gamma=10, C=1, class_weight='balanced')
cross_validation(model, 5, X_train_pca_L2, y_train[L2])

"""## Selected Parameters for L2"""

clf_L2 = svm.SVC(kernel='poly', gamma=10, C=1, class_weight='balanced')
clf_L2.fit(X_train_pca_L2, y_train[L2])
X_test_L2 = selector_pca_L2.transform(X_test)

"""# Label 03

## Performance before Feature Engineering
"""

clf = svm_classifier(X_train[L3], y_train[L3])

"""### Training Performance"""

printValidationPerformance(clf, X_train[L3], y_train[L3])

"""### Validation Performance"""

printValidationPerformance(clf, X_valid[L3], y_valid[L3])

"""## Feature Engineering"""

plt.figure(figsize=(18, 6))
sn.countplot(data=y_train, x=L3)

"""### Feature selection - univariant feature selection"""

selector_skb_L3 = SelectKBest(k=200)
X_train_skb_L3 = selector_skb_L3.fit_transform(X_train[L3], y_train[L3])

X_train_skb_L3.shape

clf_3 = svm_classifier(X_train_skb_L3, y_train[L3], class_weight='balanced')

"""#### Training Accuracy"""

printValidationPerformance(clf_3, X_train_skb_L3, y_train[L3])

"""#### Validataion Accuracy"""

printValidationPerformance(clf_3, selector_skb_L3.transform(X_valid[L3]), y_valid[L3])

"""### Feature selection - PCA"""

from sklearn.decomposition import PCA

selector_pca_L3 = PCA(n_components=0.95, svd_solver='full')
X_train_pca_L3 = pd.DataFrame(selector_pca_L3.fit_transform(X_train[L3]))

X_train_pca_L3.shape

clf_pca_L3 = svm_classifier(X_train_pca_L3, y_train[L3], class_weight='balanced')

"""#### Training Accuracy"""

printValidationPerformance(clf_pca_L3, X_train_pca_L3, y_train[L3])

"""#### Validation Accuracy"""

printValidationPerformance(clf_pca_L3, selector_pca_L3.transform(X_valid[L3]), y_valid[L3])

"""## Hyperparameter Tuning"""

clf_3 = svm.SVC()

param_grid = {
    'C': np.logspace(-3, 3, 7),
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': np.logspace(-3, 3, 7),
    'class_weight': ['balanced']
}

grid_3 = random_search(clf_3, param_grid, cv=2, n_iter=5, X_train=X_train_skb_L3, y_train=y_train[L3])

print('best parameters: ', grid_3.best_params_)

"""### Validation Accuracy"""

printValidationPerformance(grid_3.best_estimator_, selector_skb_L3.transform(X_valid[L3]), y_valid[L3])

"""## Cross Validation"""

model = grid_3.best_estimator_
cross_validation(model, 5, X_train_skb_L3, y_train[L3])

"""## Selected Parameters for L3"""

clf_L3 = svm.SVC(kernel='rbf', gamma=0.01, C=10, class_weight='balanced')
clf_L3.fit(X_train_skb_L3, y_train[L3])
X_test_L3 = selector_skb_L3.transform(X_test)

printValidationPerformance(clf_L3, selector_skb_L3.transform(X_valid[L3]), y_valid[L3])

"""# Label 04

## Performance before Feature Engineering
"""

clf = svm_classifier(X_train[L4], y_train[L4])

"""### Training Performance"""

printValidationPerformance(clf, X_train[L4], y_train[L4])

"""### Validation Performance"""

printValidationPerformance(clf, X_valid[L4], y_valid[L4])

"""## Feature Engineering"""

plt.figure(figsize=(18, 6))
sn.countplot(data=y_train, x=L4)

"""### Feature selection - univariant feature selection"""

selector_skb_L4 = SelectKBest(k=200)
X_train_skb_L4 = selector_skb_L4.fit_transform(X_train[L4], y_train[L4])

X_train_skb_L4.shape

clf_4 = svm_classifier(X_train_skb_L4, y_train[L4], class_weight='balanced')

"""#### Training Accuracy"""

printValidationPerformance(clf_4, X_train_skb_L4, y_train[L4])

"""#### Validataion Accuracy"""

printValidationPerformance(clf_4, selector_skb_L4.transform(X_valid[L4]), y_valid[L4])

"""### Feature selection - PCA"""

from sklearn.decomposition import PCA

selector_pca_L4 = PCA(n_components=0.96, svd_solver='full')
X_train_pca_L4 = pd.DataFrame(selector_pca_L4.fit_transform(X_train[L4]))

X_train_pca_L4.shape

clf_pca_L4 = svm_classifier(X_train_pca_L4, y_train[L4], class_weight='balanced')

"""#### Training Accuracy"""

printValidationPerformance(clf_pca_L4, X_train_pca_L4, y_train[L4])

"""#### Validation Accuracy"""

printValidationPerformance(clf_pca_L4, selector_pca_L4.transform(X_valid[L4]), y_valid[L4])

"""## Hyperparameter Tuning"""

clf_4 = svm.SVC()

param_grid = {
    'C': np.logspace(-3, 3, 7),
    'kernel': ['linear', 'rbf', 'poly'],
    'gamma': np.logspace(-3, 3, 7),
    'class_weight': ['balanced']
}

grid_4 = random_search(clf_4, param_grid, cv=2, n_iter=5, X_train=X_train_pca_L4, y_train=y_train[L4])

print('best parameters: ', grid_4.best_params_)

"""### Validation Accuracy"""

printValidationPerformance(grid_4.best_estimator_, selector_pca_L4.transform(X_valid[L4]), y_valid[L4])

"""## Cross Validation"""

model = svm.SVC(kernel='poly', gamma=10, C=0.01, class_weight='balanced')
cross_validation(grid_4.best_estimator_, 5, X_train_pca_L2, y_train[L2])

"""## Selected Parameters for L4"""

clf_L4 = grid_4.best_estimator_
X_test_L4 = selector_pca_L4.transform(X_test)

printValidationPerformance(clf_L4, selector_pca_L4.transform(X_valid[L4]), y_valid[L4])

"""# Prediction"""

# Label 1
pred_L1 = clf_L1.predict(X_test_L1)
# Label 2
pred_L2 = clf_L2.predict(X_test_L2)
# Label 3
pred_L3 = clf_L3.predict(X_test_L3)
# Label 4
pred_L4 = clf_L4.predict(X_test_L4)

id_list = test_df['ID']

result = {
    'ID': id_list,
    'label_1': pred_L1,
    'label_2': pred_L2,
    'label_3': pred_L3,
    'label_4': pred_L4
}

result_df = pd.DataFrame(result)

result_df.to_csv('layer_8.csv', index=False)