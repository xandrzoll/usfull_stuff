import pandas as pd
import numpy as np
import datetime
import os


src_path = r'D:\projects\SalesModel\data_samples\train'
dt_end = datetime.date(2020, 12, 1)


def load_data():
    path_data = [
        os.path.join(src_path, r'clients_gosb.xlsx'),
        os.path.join(src_path, r'nsi.xlsx'),
        os.path.join(src_path, r'sales.xlsx'),
        os.path.join(src_path, r'staff.xlsx'),
        os.path.join(src_path, r'saledays.xlsx'),
        os.path.join(src_path, r'clients.xlsx'),
    ]

    for p in path_data:
        yield pd.read_excel(p)


def create_train_dataset():
    # load all data
    clients_gosb, nsi, sales, staff, saledays, clients = load_data()

    # transform data
    # --- sales
    sales['tb'] = sales['vsp'].str[:3]
    sales = sales[sales['vsp'].str.len() > 8]
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

    # Drop carantine months
    sales = sales[
            (
                (sales['mon'] >= datetime.date(2020, 8, 1))
                | (sales['mon'] < datetime.date(2020, 4, 1))
            )
            & (sales['mon'] >= datetime.date(2019, 1, 1))
    ]


    # create columns with previous sales 2-4 month ago
    for i in range(2, 5):
        sales['sales_prev_' + str(i-1)] = sales['sales'].shift(i)
        sales.loc[(sales['vsp'].shift(i) != sales['vsp']), 'sales_prev_' + str(i-1)] = np.NaN
    sales['num_month'] = sales['month_report']
    sales['quart'] = (sales['num_month'] - 1) // 3 + 1
    sales['sales_half_last'] = sales['sales_half'].shift(1)
    sales.loc[(sales['vsp'].shift(1) != sales['vsp']), 'sales_half_last'] = np.NaN
    sales = sales.merge(
        sales.groupby(['gosb', 'mon'], as_index=False).agg({'min_up': 'min', 'max_up': 'max', }),
        on=['gosb', 'mon'],
        suffixes=['_', '']
    )

    # drop the sales which are out of range 0.1 - 0.9 percentile
    sales = sales.merge(
        sales.groupby('vsp', as_index=False)['sales'].agg(lambda x: x.quantile(0.1, axis=0)),
        on='vsp',
        suffixes=['', '_q10']
    )
    sales = sales.merge(
        sales.groupby('vsp', as_index=False)['sales'].agg(lambda x: x.quantile(0.9, axis=0)),
        on='vsp',
        suffixes=['', '_q90']
    )
    sales = sales[
        (sales['sales'] > sales['sales_q10'])
        & (sales['sales'] < sales['sales_q90'])
        & (sales['mon'] <= datetime.date(2020, 3, 1))
    ]

    # -------------

    # --- nsi
    nsi['vsp'] = nsi['DEPART_CODE'].apply(
        lambda x:
        x[3:7].strip().zfill(4) + '_' + x[7:].strip().zfill(5)
        if type(x) == str
        else ''
    )
    # -------------

    # --- staff
    staff['vsp'] = staff['urf_code'].apply(
        lambda x:
        x[x.find('_')+1:x.rfind('_')].zfill(4) + '_' + x[x.rfind('_')+1:].zfill(5)
        if type(x) == str
        else ''
    )
    staff.loc[staff['vsp'].str[:4] == '0029', 'vsp'] = '8647' + staff['vsp'].str[4:]
    staff['mon'] = staff.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    # -------------

    # --- clients_gosb
    clients_gosb['gosb'] = clients_gosb['gosb'].astype(int).astype(str).str.zfill(4)
    clients_gosb.loc[clients_gosb['gosb'] == '0029', 'gosb'] = '8647'
    clients_gosb['mon'] = clients_gosb.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    clients_gosb = clients_gosb.sort_values(['gosb', 'mon'])
    # for i in range(1, 13):
    #     clients_gosb['avg_clients_prev_' + str(i)] = clients_gosb['avg_clients'].shift(i)
    #     clients_gosb.loc[(clients_gosb['gosb'].shift(1) != clients_gosb['gosb']), 'avg_clients_prev_' + str(i)] = np.NaN
    # clients_gosb = clients_gosb[pd.notnull(clients_gosb['avg_clients_prev_12'])]
    # for i in range(2, 13):
    #     clients_gosb['avg_clients_delta_' + str(i)] = (clients_gosb['avg_clients_prev_' + str(i)] - clients_gosb[
    #         'avg_clients_prev_' + str(i - 1)]) / clients_gosb['avg_clients_prev_' + str(i)]

    # create columns for client flow in gosb from 2-12 month ago
    for i in range(2, 13):
        clients_gosb['avg_clients_' + str(i-1)] = clients_gosb['avg_clients'].shift(i)
        clients_gosb.loc[(clients_gosb['gosb'].shift(i) != clients_gosb['gosb']), 'avg_clients_' + str(i-1)] = np.NaN
    # clients_gosb['avg_clients_13'] = clients_gosb['avg_clients'].shift(13)
    # clients_gosb.loc[(clients_gosb['gosb'].shift(13) != clients_gosb['gosb']), 'avg_clients_delta_12'] = np.NaN
    # clients_gosb['avg_clients_delta_2'] = (clients_gosb['avg_clients'].shift(2) - clients_gosb['avg_clients'].shift(3)) / clients_gosb['avg_clients'].shift(3)
    # clients_gosb.loc[(clients_gosb['gosb'].shift(13) != clients_gosb['gosb']), 'avg_clients_delta_2'] = np.NaN
    # clients_gosb['avg_clients_delta_3'] = (clients_gosb['avg_clients'].shift(3) - clients_gosb['avg_clients'].shift(2)) / clients_gosb['avg_clients'].shift(2)
    # clients_gosb.loc[(clients_gosb['gosb'].shift(13) != clients_gosb['gosb']), 'avg_clients_delta_2'] = np.NaN
    # -------------

    # --- clients vsp
    clients['gosb'] = clients['gosb'].astype(int).astype(str).str.zfill(4)
    clients.loc[clients['gosb'] == '0029', 'gosb'] = '8647'
    clients['vsp'] = clients['gosb'] + '_' + clients['VSP'].astype(int).astype(str).str.zfill(5)
    clients['mon'] = clients.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    clients = clients.sort_values(['vsp', 'mon'])
    for i in range(2, 5):
        clients['clients_' + str(i-1)] = clients['all_clients'].shift(i)
        clients.loc[(clients['vsp'].shift(i) != clients['vsp']), 'clients_' + str(i-1)] = np.NaN
    # -------------

    # --- saledays
    saledays.loc[saledays['vsp'].str.len() > 8, 'vsp'] = saledays['vsp'].apply(
        lambda x:
        x[x.find('_')+1:x.rfind('_')].zfill(4) + '_' + x[x.rfind('_')+1:].zfill(5)
        if type(x) == str
        else ''
    )
    saledays.loc[saledays['vsp'].str[:4] == '0029', 'vsp'] = '8647' + saledays['vsp'].str[4:]
    saledays['mon'] = saledays.apply(lambda x: datetime.date(x['year_report'], x['month_report'], 1), axis=1)
    # -------------

    # --- merge data
    dataset = sales.merge(
        nsi,
        on='vsp',
        how='left'
    )
    dataset = dataset.merge(
        staff,
        on=['vsp', 'mon'],
        how='left'
    )
    dataset = dataset.merge(
        clients_gosb,
        on=['gosb', 'mon'],
        how='left'
    )
    dataset = dataset.merge(
        clients,
        on=['vsp', 'mon'],
        how='left'
    )
    dataset = dataset.merge(
        saledays,
        on=['vsp', 'mon'],
        how='left'
    )

    # if vsp have no staff in current month get the previous
    for pos in ['mp_staff', 'kbp_staff', 'rvsp_staff', 'zrvsp_staff', 'smo_staff', 'vmo_staff', 'full_staff']:
        dataset.loc[pd.isnull(dataset[pos]) & (dataset['vsp'] == dataset['vsp'].shift(1)), pos] = dataset[pos].shift(1)
        dataset.loc[pd.isnull(dataset[pos]) & (dataset['vsp'] == dataset['vsp'].shift(1)), pos] = dataset[pos].shift(1)

    dataset = dataset[dataset['mon'] < dt_end]

    dataset.rename(columns={'gosb_x': 'gosb'}, inplace=True)

    use_cols = ['sales', 'vsp', 'sales_half', 'sales_prev_1', 'sales_prev_2', 'sales_prev_3',
                'num_month', 'quart', 'min_up', 'max_up', 'mp_staff', 'kbp_staff', 'rvsp_staff', 'zrvsp_staff',
                'smo_staff', 'vmo_staff', 'full_staff', 'avg_clients_1', 'avg_clients_2', 'avg_clients_3',
                'avg_clients_4', 'avg_clients_5', 'avg_clients_6', 'avg_clients_7', 'avg_clients_8', 'avg_clients_9',
                'avg_clients_10', 'avg_clients_11', 'clients_1', 'clients_2', 'clients_3',
                'workdays_mp', 'workdays_kbp',
                'gosb', 'DEPART_LOCTYPE', 'DEPART_LOCSTATUS',
                ]

    dataset = dataset.dropna()

    return dataset[use_cols]


if __name__ == '__main__':
    data_train = create_train_dataset()
    # gosb_vals = data_train.gosb.unique()
