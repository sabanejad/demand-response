def household_mean_daily_consumption(df):
    df = df.groupby([df['date_time'].dt.normalize(), df['house_id']]).sum().rename(columns={'KWH/hh': 'KWH/D'})
    df['treated'] = df['treated'].astype('bool')
    df = df.groupby([df.index.get_level_values(0), 'treated']).mean()
    return df['KWH/D'].unstack()

# returns annual consumption by the treatment group and control group, respectively
def annual_consumption(df):
    df = df.groupby([df['date_time'].dt.year, df['house_id']]).sum().rename(columns={'KWH/hh': 'KWH/Y'})
    df['treated'] = df['treated'].astype('bool')
    df = df.groupby([df.index.get_level_values(0), 'treated']).mean()
    df = df['KWH/Y'].unstack()
    return df[True].values[0], df[False].values[0]

def get_consumption_demographic(df, dem):
    dem_df = df.loc[df['acorn_category'] == dem].reset_index(drop=True)
    dem_df.reset_index(drop=True, inplace=True)
    return dem_df

def transform_KWH(n):
    print('= ', n * 1000 * 48 / 234, 'hours of TV')
    print('= ', n * 1000 * 48 / 225, 'hours of fridge')
    print('= ', n * 1000 * 48 / 255, 'hours of washing machine')
    print('= ', n * 1000 * 48 / 2790, 'hours of dryer')
    print('= ', n * 1000 * 48 / 3500, 'hours of AC')

def find_top_components(s, n): 
    sum = 0
    power = (s * s).sum()
    for i in range(len(s)):
        sum += s[i] ** 2
        if sum >= n * power:
            return i
            break

def get_matrices(t1, c1, t2, c2, x):

    a1, b1, a2, b2 = get_alpha_beta(t1, c1, t2, c2)
    print('before anything', a1.shape, b1.shape, a2.shape, b2.shape)

    a1 = clean_house(a1, x)
    b1 = clean_house(b1, x)
    a2 = clean_house(a2, x)
    b2 = clean_house(b2, x)
    print('after cleaning', a1.shape, b1.shape, a2.shape, b2.shape)

    a1, b1, a2, b2 = house_intersect(a1, b1, a2, b2)
    print('after house intersection', a1.shape, b1.shape, a2.shape, b2.shape)

    return a1, b1, a2, b2

# clean the data, remove houses that have more than x% of their hh data missing
def clean_house(mat, x):
    missing = mat.loc[:, mat.isna().sum(axis=0) / mat.shape[1] > 0.01].columns
    return mat.drop(columns=missing)

def split_t_c(df):

    treatment = df.loc[df['treated']]
    control = df.loc[~df['treated']]

    return treatment, control

def unique_house_per_hh(df):
    return df.groupby(df['date_time'].dt.normalize())['house_id'].nunique()

def household_mean_daily_consumption(df):
    df = df.groupby([df['date_time'].dt.normalize(), df['house_id']]).sum().rename(columns={'KWH/hh': 'KWH/D'})
    df['treated'] = df['treated'].astype('bool')
    df = df.groupby([df.index.get_level_values(0), 'treated']).mean()
    return df['KWH/D'].unstack()

def get_alpha_beta(t1, c1, t2, c2):

    a1 = c1.pivot_table(index='date_time', columns='house_id', values='KWH/hh')
    b1 = t1.pivot_table(index='date_time', columns='house_id', values='KWH/hh')
    
    a2 = c2.pivot_table(index='date_time', columns='house_id', values='KWH/hh')
    b2 = t2.pivot_table(index='date_time', columns='house_id', values='KWH/hh')
    # a_2013.merge(b_2013, how='outer', on='date_time')
    
    return a1, b1, a2, b2

def impute(arr, f, axis):
    import numpy as np
    out = arr.copy()
    np.copyto(out, f(arr, axis=axis, keepdims=True), where=np.isnan(arr))
    return out

def get_subset(time, socio):
    actual = b_2013_.loc[b_2013_.index.isin(time), b_2013_.columns.isin(socio)]
    predicted = b_2013_tilde_.loc[b_2013_tilde_.index.isin(time), b_2013_tilde_.columns.isin(socio)]
    return np.median((actual - predicted) / predicted)

# takes the mean across all houses in each group for each hh
def mean_over_houses_per_hh(df):
    df = df.groupby(['treated', 'date_time']).mean(['KWH/hh'])
    return df.unstack('treated')

# takes the mean across all houses in each group for each hh
def mean_over_houses_per_hh_price(df):
    df = df.groupby(['treated', 'date_time'])['p/hh'].mean()
    return df.unstack('treated')

def find_mean_peryear(df, col):
    # sum hh measurements per house per day
    # divide by the number of unique hh measurements per house per day
    # = unique avg consumption value per house per day
    avg_consumption_perhouse_perday = df.groupby([df['date_time'].dt.normalize(), 'house_id'])[col].mean().reset_index()
    # now sum all these unique values for all houses
    # and divide by number of unique houses for which there is data for that day
    # = a unique value per day
    # return avg_consumption_perhouse_perday.groupby(['date_time'])[col].mean().mean()
    return avg_consumption_perhouse_perday.groupby(['date_time'])[col].mean()

def house_intersect(a1, b1, a2, b2):

    treatment_houses = set(b1.columns).intersection(set(b2.columns))
    # control_houses = set(c2['house_id']).intersection(set(c1['house_id']))
    control_houses = set(a1.columns).intersection(set(a2.columns))
#     treatment_times_2012 = set(df_2013_treatment['date_time'] - np.timedelta64(365,'D')).intersection(set(df_2012_treatment['date_time']))
# #     control_times_2012 = set(df_2013_control['date_time'] - np.timedelta64(365,'D')).intersection(set(df_2012_control['date_time']))
# #     treatment_times_2013 = set(df_2013_treatment['date_time']).intersection(set(df_2012_treatment['date_time'] + np.timedelta64(365,'D')))
# #     control_times_2013 = set(df_2013_control['date_time']).intersection(set(df_2012_control['date_time'] + np.timedelta64(365,'D')))

    # t1 = t1.loc[t1['house_id'].isin(treatment_houses)]
    # c1 = c1.loc[c1['house_id'].isin(control_houses)]
    # t2 = t2.loc[t2['house_id'].isin(treatment_houses)]
    # c2 = c2.loc[c2['house_id'].isin(control_houses)]
    a1 = a1.loc[a1.index, a1.columns.isin(control_houses)]
    b1 = b1.loc[b1.index, b1.columns.isin(treatment_houses)]
    a2 = a2.loc[a2.index, a2.columns.isin(control_houses)]
    b2 = b2.loc[b2.index, b2.columns.isin(treatment_houses)]
    
    return a1, b1, a2, b2
#     t2 = t2.loc[(df_2013_treatment['house_id'].isin(treatment_houses))
#                                           & (df_2013_treatment['date_time'].isin(treatment_times_2013))]
#     c1 = c1.loc[(df_2012_control['house_id'].isin(control_houses))
#                                           & (df_2012_control['date_time'].isin(control_times_2012))]
#     c2 = c2.loc[(df_2013_control['house_id'].isin(control_houses))
#                                           & (df_2013_control['date_time'].isin(control_times_2013))]
    
#     df_2012_treatment = df_2012_treatment.loc[(df_2012_treatment['house_id'].isin(treatment_houses))]
#     df_2013_treatment = df_2013_treatment.loc[(df_2013_treatment['house_id'].isin(treatment_houses))]
#     df_2012_control = df_2012_control.loc[(df_2012_control['house_id'].isin(control_houses))]
#     df_2013_control = df_2013_control.loc[(df_2013_control['house_id'].isin(control_houses))]
    
# #     print(len(treatment_houses), len(control_houses))
# #     print(df_2012_treatment.shape, df_2013_treatment.shape, df_2012_control.shape, df_2013_control.shape)
# #     print(df_2012_treatment['house_id'].nunique(), df_2013_treatment['house_id'].nunique(), 
# #           df_2012_control['house_id'].nunique(), df_2013_control['house_id'].nunique())
    
#     return df_2012_treatment, df_2013_treatment, df_2012_control, df_2013_control