import sys

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import ElasticNet, Lars, LassoLars, OrthogonalMatchingPursuit, BayesianRidge
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ARDRegression, LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

VECTORS_AGES_PATH = r'D:\Data\Linkage\FL\FL18\tweets\vecs_ages_200.csv'


def get_label(age, range_size):
    if age % range_size == 0:
        l = age - range_size + 1
        h = age
        label = str(l) + '-' + str(h)
    else:
        l = range_size * (age // range_size) + 1
        h = l + range_size - 1
        label = str(l) + '-' + str(h)
    return label


def get_custom_label(age):
    if age <= 18:
        return '<=18'
    elif age >= 19 and age <= 22:
        return '19-22'
    elif age >= 23 and age <= 33:
        return '23-33'
    elif age >= 34 and age <= 45:
        return '34-45'
    else:
        return '>=46'


def linear_regression(X, Y):
    model = LinearRegression()
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('linear regression mae: {:0.2f}'.format(mae))


def ridge_regression(X, Y):
    model = Ridge(alpha=0.5)
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('ridge regression mae: {:0.2f}'.format(mae))


def lasso_regression(X, Y):
    model = Lasso(alpha=0.1)
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('lasso regression mae: {:0.2f}'.format(mae))


def elasticnet_regression(X, Y):
    model = ElasticNet()
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('elasticnet regression mae: {:0.2f}'.format(mae))


def lars_regression(X, Y):
    model = Lars()
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('lars regression mae: {:0.2f}'.format(mae))


def lassolars_regression(X, Y):
    model = LassoLars(alpha=0.1)
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('lasso lars regression mae: {:0.2f}'.format(mae))


def orthmatchpur_regression(X, Y):
    model = OrthogonalMatchingPursuit()
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('orthogonal matching pursuit regression mae: {:0.2f}'.format(mae))


def bayesianridge_regression(X, Y):
    model = BayesianRidge()
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('bayesian ridge regression mae: {:0.2f}'.format(mae))


def autorelevancedeter_regression(X, Y):
    model = ARDRegression()
    nmaes = cross_val_score(estimator=model, X=X, y=Y, cv=10, n_jobs=4, scoring='neg_mean_absolute_error')
    mae = -1 * nmaes.mean()
    print('bayesian ridge regression mae: {:0.2f}'.format(mae))


def adaboost_classification(X, Y, n_fold):
    print('started adaboost')
    model = AdaBoostClassifier(n_estimators=50, random_state=0)
    accs = cross_val_score(estimator=model, X=X, y=Y, cv=n_fold, n_jobs=4, scoring='accuracy')
    acc = accs.mean()
    print('adaboost classification accuracy: {:0.2f}'.format(acc))


def multinomialnb_classification(X, Y, n_fold):
    print('started multinomialnb')
    model = MultinomialNB()
    accs = cross_val_score(estimator=model, X=X, y=Y, cv=n_fold, n_jobs=4, scoring='accuracy')
    acc = accs.mean()
    print('multinomialnb classification accuracy: {:0.2f}'.format(acc))


def randomforest_classification(X, Y, n_fold):
    print('started random-forest')
    model = RandomForestClassifier(n_estimators=50, max_depth=10)
    accs = cross_val_score(estimator=model, X=X, y=Y, cv=n_fold, n_jobs=4, scoring='accuracy')
    acc = accs.mean()
    print('random-forest classification accuracy: {:0.2f}'.format(acc))


def logregression_classification(X, Y, n_fold):
    print('started logistic-regression')
    model = LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial')
    accs = cross_val_score(estimator=model, X=X, y=Y, cv=n_fold, n_jobs=4, scoring='accuracy')
    acc = accs.mean()
    print('logistic-regression classification accuracy: {:0.2f}'.format(acc))


def kneighbors_classification(X, Y, n_fold):
    print('started kneighbors')
    model = KNeighborsClassifier(n_neighbors=10)
    accs = cross_val_score(estimator=model, X=X, y=Y, cv=n_fold, n_jobs=4, scoring='accuracy')
    acc = accs.mean()
    print('kneighbors classification accuracy: {:0.2f}'.format(acc))


def svc_classification(X, Y, n_fold):
    print('started svc')
    model = SVC(gamma='auto')
    accs = cross_val_score(estimator=model, X=X, y=Y, cv=n_fold, n_jobs=4, scoring='accuracy')
    acc = accs.mean()
    print('svc classification accuracy: {:0.2f}'.format(acc))


if __name__ == '__main__':
    dataset = pd.read_csv(VECTORS_AGES_PATH, header=None)
    X = dataset.iloc[:, :-1].values
    Y = dataset.iloc[:, -1].values
    Y_labels = list(map(lambda x: get_custom_label(age=x), Y))

    classifiers = [adaboost_classification,
                   multinomialnb_classification,
                   randomforest_classification,
                   logregression_classification,
                   kneighbors_classification,
                   svc_classification]

    classifier_index = int(sys.argv[1])

    classifiers[classifier_index](X=X, Y=Y_labels, n_fold=5)
