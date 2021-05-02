import pandas as pd
import numpy as np
import datetime
import os


src_path = r'D:\projects\SalesModel\data_samples\predict'
num_month = 4
quart = 2
work_days = 30
gosb_vals = [
    '0017', '1790', '1791', '1806', '5221', '5940', '6984', '6991',
    '7003', '8047', '8369', '8586', '8588', '8589', '8592', '8593',
    '8594', '8595', '8596', '8597', '8599', '8601', '8604', '8605',
    '8606', '8607', '8608', '8609', '8610', '8611', '8612', '8613',
    '8614', '8615', '8617', '8618', '8619', '8620', '8621', '8622',
    '8623', '8624', '8626', '8627', '8628', '8629', '8630', '8634',
    '8637', '8638', '8639', '8640', '8646', '8647', '9013', '9038',
    '9040', '9042', '9055'
]


def load_data():
    path_data = [
        os.path.join(src_path, r'clients_gosb.xlsx'),
        os.path.join(src_path, r'nsi.xlsx'),
        os.path.join(src_path, r'sales.xlsx'),
        os.path.join(src_path, r'staff.xlsx'),
        os.path.join(src_path, r'clients.xlsx'),
        os.path.join(src_path, r'norm_staff.xlsx'),
    ]

    for p in path_data:
        yield pd.read_excel(p)


def create_predict_dataset():
    # Load all data
    clients_gosb, nsi, sales, staff, clients, norm_staff = load_data()

    # Create new dataset from 3-month-sales and norm_staff mp
    sales_month = sales[['year_report', 'month_report']].drop_duplicates().sort_values(
        ['year_report', 'month_report'], ascending=[False, False]).head(3).reset_index(drop=True)
    dataset = sales[
        sales['year_report'].isin(sales_month['year_report'])
        & sales['month_report'].isin(sales_month['month_report'])
    ]['vsp'].drop_duplicates()

    dataset = dataset.append(norm_staff['urf_code_actual'], ignore_index=True)
    dataset = pd.DataFrame(dataset.drop_duplicates().reset_index(drop=True), columns=['vsp'])

    # Merge norm mp and kbp
    dataset = dataset.merge(
        norm_staff,
        right_on='urf_code_actual',
        left_on='vsp',
        how='left'
        )[['vsp', 'mp_staff', 'kbp_staff']]

    # Merge last staff data
    dataset = dataset.merge(
        staff,
        right_on='urf_code',
        left_on='vsp',
        how='left',
        suffixes=['', '2']
        )

    # Transform vsp code by mask 0000_00000
    dataset['tb'] = dataset['vsp'].str[:3]
    dataset['vsp'] = dataset['vsp'].apply(
        lambda x:
        x[x.find('_')+1:x.rfind('_')].zfill(4) + '_' + x[x.rfind('_')+1:].zfill(5)
        if type(x) == str
        else ''
    )
    dataset['gosb'] = dataset['vsp'].str[:4]
    dataset['gosb'] = dataset['gosb'].apply(lambda x: x if x in gosb_vals else '9038')

    # transform sales data
    sales.loc[:, 'vsp'] = sales['vsp'].apply(
        lambda x:
        x[x.find('_')+1:x.rfind('_')].zfill(4) + '_' + x[x.rfind('_')+1:].zfill(5)
        if type(x) == str
        else ''
    )
    sales.loc[sales['vsp'].str[:4] == '0029', 'vsp'] = '8647' + sales['vsp'].str[4:]
    sales['gosb'] = sales['vsp'].str[:4]
    sales['mon'] = sales.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    sales = sales.sort_values(['vsp', 'mon'])

    # create columns with previous sales 2-4 month ago
    for i in range(1, 4):
        sales['sales_prev_' + str(i)] = sales['sales'].shift(i)
        sales.loc[(sales['vsp'].shift(i) != sales['vsp']), 'sales_prev_' + str(i)] = np.NaN
    sales['sales_half_last'] = sales['sales_half'].shift(1)
    sales.loc[(sales['vsp'].shift(1) != sales['vsp']), 'sales_half_last'] = np.NaN
    sales = sales.merge(
        sales.groupby(['gosb', 'mon'], as_index=False).agg({'min_up': 'min', 'max_up': 'max', }),
        on=['gosb', 'mon'],
        suffixes=['_', '']
    )

    sales = sales[
        (sales['year_report'] == sales_month.iloc[0, 0])
        & (sales['month_report'] == sales_month.iloc[0, 1])
    ][['vsp', 'sales', 'sales_half', 'sales_prev_1', 'sales_prev_2', 'sales_prev_3', 'min_up', 'max_up']]
    sales = sales.drop_duplicates()

    # Merge sales to dataset
    dataset = dataset.merge(
        sales,
        on='vsp',
        how='left',
        suffixes=['', '_sales']
    )
    # -------------

    # --- nsi
    nsi['vsp'] = nsi['DEPART_CODE'].apply(
        lambda x:
        x[3:7].strip().zfill(4) + '_' + x[7:].strip().zfill(5)
        if type(x) == str
        else ''
    )
    dataset = dataset.merge(
        nsi,
        on='vsp',
        how='left',
        suffixes=['', '_nsi']
    )
    # -------------

    # --- clients_gosb
    clients_gosb['gosb'] = clients_gosb['gosb'].astype(int).astype(str).str.zfill(4)
    clients_gosb.loc[clients_gosb['gosb'] == '0029', 'gosb'] = '8647'
    clients_gosb['mon'] = clients_gosb.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    clients_gosb = clients_gosb.sort_values(['gosb', 'mon'])

    # create columns for client flow in gosb from 2-12 month ago
    for i in range(1, 12):
        clients_gosb['avg_clients_' + str(i)] = clients_gosb['avg_clients'].shift(i)
        clients_gosb.loc[(clients_gosb['gosb'].shift(i) != clients_gosb['gosb']), 'avg_clients_' + str(i)] = np.NaN

    clients_gosb = clients_gosb[
        (clients_gosb['year_report'] == sales_month.iloc[0, 0])
        & (clients_gosb['month_report'] == sales_month.iloc[0, 1])
        ]

    dataset = dataset.merge(
        clients_gosb,
        on='gosb',
        how='left',
        suffixes=['', '_clients_gosb']
    )
    # -------------

    # --- clients vsp
    clients.rename(columns={'VSP': 'vsp'}, inplace=True)
    clients['gosb'] = clients['gosb'].astype(int).astype(str).str.zfill(4)
    clients.loc[clients['gosb'] == '0029', 'gosb'] = '8647'
    clients['vsp'] = clients['gosb'] + '_' + clients['vsp'].astype(int).astype(str).str.zfill(5)
    clients['mon'] = clients.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    clients = clients.sort_values(['vsp', 'mon'])
    for i in range(1, 4):
        clients['clients_' + str(i)] = clients['all_clients'].shift(i)
        clients.loc[(clients['vsp'].shift(i) != clients['vsp']), 'clients_' + str(i)] = np.NaN

    clients = clients[
        (clients['year_report'] == sales_month.iloc[0, 0])
        & (clients['month_report'] == sales_month.iloc[0, 1])
        ]

    dataset = dataset.merge(
        clients,
        on='vsp',
        how='left',
        suffixes=['', '_clients_vsp']
    )
    # -------------

    # Add columns which was in the train data
    dataset['workdays_mp'] = dataset['mp_staff'] * work_days
    dataset['workdays_kbp'] = dataset['kbp_staff'] * work_days
    dataset['num_month'] = num_month
    dataset['quart'] = quart
    # -------------

    use_cols = ['vsp', 'sales_half', 'sales_prev_1', 'sales_prev_2', 'sales_prev_3',
                'num_month', 'quart', 'min_up', 'max_up', 'mp_staff', 'kbp_staff', 'rvsp_staff', 'zrvsp_staff',
                'smo_staff', 'vmo_staff', 'full_staff', 'avg_clients_1', 'avg_clients_2', 'avg_clients_3',
                'avg_clients_4', 'avg_clients_5', 'avg_clients_6', 'avg_clients_7', 'avg_clients_8', 'avg_clients_9',
                'avg_clients_10', 'avg_clients_11', 'clients_1', 'clients_2', 'clients_3',
                'workdays_mp', 'workdays_kbp',
                'gosb', 'DEPART_LOCTYPE', 'DEPART_LOCSTATUS',
                ]

    dataset = fill_na(dataset[use_cols])

    return dataset


def fill_na(dataset: pd.DataFrame):
    cols = dataset.columns

    # for col in ['sales_half', 'sales_prev_2', 'sales_prev_3', 'sales_prev_4', 'min_up', 'max_up']:
    #     if col in cols:
    #         fill_data = dataset.groupby('gosb', as_index=False)[col].mean().reset_index(drop=True)
    #         dataset[col] = dataset.apply(
    #             lambda x: fill_data[fill_data['gosb'] == x['gosb']][col].values[0] if pd.isnull(x[col]) else x[col], axis=1)

    for col in ['mp_staff', 'kbp_staff', 'rvsp_staff', 'zrvsp_staff', 'smo_staff', 'vmo_staff', 'full_staff']:
        if col in cols:
            dataset[col].fillna(0, inplace=True)

    for col in ['DEPART_LOCTYPE', 'DEPART_LOCSTATUS', 'DEPART_SUBJECT']:
        if col in cols:
            fill_data = dataset.groupby(['gosb', col], as_index=False)['vsp'].count().sort_values('vsp', ascending=False)
            fill_data = fill_data.groupby('gosb', as_index=False)[col].first()
            # In here we have problem. Wrong gosb are not in fill_data and in lambda .values returns empty list.
            dataset[col] = dataset.apply(
                lambda x: (list(fill_data[fill_data['gosb'] == x['gosb']][col].values) + [''])[0]
                if pd.isnull(x[col]) else x[col],
                axis=1)

    for col in ['clients_1', 'clients_2', 'clients_3', 'sales_half', 'sales_prev_1', 'sales_prev_2', 'sales_prev_3', 'min_up', 'max_up']:
        if col in cols:
            fill_data = dataset.groupby(['gosb', 'DEPART_LOCSTATUS'], as_index=False)[col].mean().reset_index(drop=True)
            dataset[col] = dataset.apply(
                lambda x:
                    fill_data[
                        (fill_data['gosb'] == x['gosb']) & (fill_data['DEPART_LOCSTATUS'] == x['DEPART_LOCSTATUS'])
                    ][col].values[0]
                    if pd.isnull(x[col]) else x[col],
                axis=1)

    # fill null for numeric and string data
    dataset = dataset.fillna(0)

    # dataset = dataset[
    #     list(dataset.dtypes[dataset.dtypes == object].index)
    # ].fillna(method='ffill', inplace=True)

    return dataset


if __name__ == '__main__':
    data_predict = create_predict_dataset()
