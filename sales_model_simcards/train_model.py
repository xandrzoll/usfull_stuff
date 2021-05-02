import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error # scikit-learn

from train_data import create_train_dataset


def train_model(data: pd.DataFrame):
    y = data.iloc[:, 0]
    X = data.iloc[:, 2:]
    
    category_cols = list(X.dtypes[X.dtypes == 'object'].index)
    X = pd.get_dummies(X, columns=category_cols)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=43, shuffle=True)
    print('Размер обучающей выборки: {}\nРазмер тестовой выборки: {}'.format(len(X_train), len(X_test)))

    params = {
        'n_estimators': [800, 1200, 1500],
        'max_depth': [5, 15, 30],
        'min_samples_leaf': [1, 5, 10],
        'random_state': [42],
        'n_jobs': [-1],
    }

    # print('Подбираю параметры модели')
    # clf = GridSearchCV(RandomForestRegressor(), params, cv=5, scoring='r2')
    # clf.fit(X_train, y_train)
    #
    # print('Наилучшие параметры:', clf.best_params_)
    # print('Наилучший результат:', clf.best_score_)
    #
    # rf = clf.best_estimator_
    # rf.fit(X_train, y_train)

    rf = RandomForestRegressor()
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    print('R2 на тестовой выборке:', r2_score(y_test, y_pred))
    print('MAE на тестовой выборке:', mean_absolute_error(y_test, y_pred))

    pickle.dump(rf, open('model2.pkl', 'wb'))


def main():
    data = create_train_dataset()
    train_model(data)


if __name__ == '__main__':
    main()

