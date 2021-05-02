import pandas as pd

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score, accuracy_score

from concurrent.futures import ProcessPoolExecutor, as_completed


def run_model(pos: str, data: pd.DataFrame, target):
    X = data[data['Группа'] == pos]

    corr = X.iloc[:, 3:].corr()['Успешность'][1:]
    corr = corr[abs(corr) > 0.0].sort_values(ascending=True)
    corr = corr.iloc[corr.abs().argsort()[::-1]]

    y = X.iloc[:, 3]
    X = X.iloc[:, 4:]
    # X = X.iloc[:, 50:]

    sss = StratifiedShuffleSplit(n_splits=1, test_size=.2)
    for trn_idx, tst_idx in sss.split(X, y):
        X_train, y_train = X.iloc[trn_idx, :], y.iloc[trn_idx]
        X_test, y_test = X.iloc[tst_idx, :], y.iloc[tst_idx]

    params = {
        'n_estimators': [500, 800, 1000, 1200, 1500, 2000, 2500],
        'max_depth': [5, 15, 30, 50],
        'min_samples_leaf': [1, 5, 10, 15],
        'random_state': [42],
        'n_jobs': [-1],
    }

    clf = GridSearchCV(RandomForestClassifier(), params, cv=5, scoring='roc_auc')
    clf.fit(X_train, y_train)

    # print(pos, clf.best_params_, clf.best_score_)

    rf = clf.best_estimator_

    fi = pd.DataFrame(zip(rf.feature_importances_, X_train.columns)).sort_values([0], ascending=False)

    rf.fit(X_train, y_train)
    roc_auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])
    accuracy = accuracy_score(y_test, rf.predict(X_test))

    pr_rf = rf.predict_proba(target.iloc[:, 4:])
    # target['predict' + '_' + pos] = pr_rf[:, 1]

    return {'pos': pos, 'data': pr_rf[:, 1], 'roc_auc': roc_auc, 'accuracy': accuracy, 'corr': corr, 'fi': fi}


def main(multy=True):
    data = pd.read_excel(r'D:\projects\Useful_Stuffs\model_mpp\список4.xlsx', 'Лист1', skiprows=2)

    data = data[(data['gender'] != 0) & (data['no_cash'] != 0)]
    data['gender'] = data['gender'].map({'F': 1, 'M': 0})
    data['Успешность'] = data['Успешность'].map({'Успешные': 1, 'Не успешные': 0, 'Целевая': 2})
    data.fillna(0, inplace=True)

    # target = data[data['Группа'] == 'МПП']
    target = data.copy()
    data = data[data['Группа'] != 'МПП']

    results = []

    if not multy:
        for pos in data['Группа'].unique():
            print('Running model for', pos)
            result = run_model(pos, data, target)
            with open(r'D:\projects\Useful_Stuffs\model_mpp\info2.txt', 'a') as file:
                file.write('='*40)
                file.write('\n' + pos + '\n')
                file.write('Roc_auc:' + str(result['roc_auc']) + '\n')
                file.write('Accuracy:' + str(result['accuracy']) + '\n')
                file.write('\n___ Корреляция: ___\n\n')

                for ind, val in zip(result['corr'].index, result['corr'].values):
                    file.write(str(ind) + '\t\t' + str(val) + '\n')

                file.write('\n___ Важность признаков: ___\n\n')
                for i in range(len(result['fi'])):
                    file.write(str(result['fi'].iloc[i, 1]) + '\t\t' + str(result['fi'].iloc[i, 0]) + '\n')

    else:
        with ProcessPoolExecutor(max_workers=4) as executor:
            for pos in data['Группа'].unique():
                print('Running model for', pos)
                result = executor.submit(run_model, pos, data, target)
                results.append(result)

            for f in as_completed(results):
                target[f.result()['pos']] = f.result()['data']
                print(f.result()['pos'])
                print('Roc_auc:', f.result()['roc_auc'])
                print('Corr:', f.result()['corr'])
                print('Features Importance:', f.result()['fi'])
                print('='*20)
                with open(r'D:\projects\Useful_Stuffs\model_mpp\info2.txt', 'a') as file:
                    file.write(f.result()['pos'] + '\n\n')
                    file.write('Roc_auc:' + str(f.result()['roc_auc']) + '\n')
                    file.write('Accuracy:' + str(f.result()['accuracy']))
                    file.write('\n\n___ Корреляция: ___\n')
                    for ind, val in zip(f.result()['corr'].index, f.result()['corr'].values):
                        file.write(str(ind) + '\t\t' + str(val) + '\n')
                    file.write('\n___ Важность признаков: ___\n')
                    for i in range(len(f.result()['fi'])):
                        file.write(str(f.result()['fi'].iloc[i, 1]) + '\t\t' + str(f.result()['fi'].iloc[i, 0]) + '\n')
                    file.write('=' * 40)
                    file.write('\n\n\n')

    target.to_excel(r'D:\projects\Useful_Stuffs\model_mpp\target3.xlsx')


if __name__ == '__main__':
    main(multy=True)
