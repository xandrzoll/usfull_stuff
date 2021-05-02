import pandas as pd
import numpy as np
import pickle

from predict_data import create_predict_dataset


def predict():
    data = create_predict_dataset()

    out_data = pd.DataFrame(data.iloc[:, 0], columns=['vsp'])
    X = data.iloc[:, 1:]

    category_cols = list(X.dtypes[X.dtypes == 'object'].index)
    X = pd.get_dummies(X, columns=category_cols)

    model = pickle.load(open('model.pkl', 'rb'))

    out_data['sales_predict'] = model.predict(X)
    out_data['sales_predict'] = out_data['sales_predict'].apply(np.ceil)
    out_data.to_excel('predict_sales_for_vsp_04-2021.xlsx', index=False)


if __name__ == '__main__':
    predict()
