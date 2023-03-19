import os

from catboost import Pool
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from catboost import CatBoostRegressor


def main(path):
    df = pd.read_csv('train.csv')

    df = df.rename({'Date of Joining': 'Date_of_Joining',
                    'Company Type': 'Service',
                    'WFH Setup Available': 'remotely',
                    'Resource Allocation': 'Resource_Allocation',
                    'Mental Fatigue Score': 'Mental_Fatigue_Score',
                    'Burn Rate': 'Burn_Rate'
                    }, axis=1)

    df['Gender'] = df['Gender'].replace({'Male': 1, 'Female': 0})
    df['Service'] = df['Service'].replace({'Service': 1, 'Product': 0})
    df['remotely'] = df['remotely'].replace({'Yes': 1, 'No': 0})
    df.dropna(subset=['Burn_Rate'], axis=0, inplace=True)

    median_imputer_bins = df.copy()
    Resourse_bins = median_imputer_bins.groupby('Designation')
    Resourse_bins.Resource_Allocation.median()

    median_imputer_bins.Resource_Allocation = Resourse_bins.Resource_Allocation.apply(lambda x: x.fillna(x.median()))
    median_imputer_bins.Resource_Allocation.isna().sum()

    df['Resource_Allocation'] = median_imputer_bins['Resource_Allocation']

    Mental_bins = median_imputer_bins.groupby('Resource_Allocation')
    Mental_bins.Mental_Fatigue_Score.median()
    median_imputer_bins.Mental_Fatigue_Score = Mental_bins.Mental_Fatigue_Score.apply(lambda x: x.fillna(x.median()))
    median_imputer_bins.Resource_Allocation.isna().sum()
    df['Mental_Fatigue_Score'] = median_imputer_bins['Mental_Fatigue_Score']

    X = ['Date_of_Joining', 'Gender', 'Service', 'remotely', 'Designation', 'Resource_Allocation',
         'Mental_Fatigue_Score']
    cat_features = ['Date_of_Joining']
    y = ['Burn_Rate']

    train, test = train_test_split(df, train_size=0.6, random_state=42)
    val, test = train_test_split(test, train_size=0.5, random_state=42)

    train_data = Pool(data=train[X],
                      label=train[y],
                      cat_features=cat_features
                      )

    val_data = Pool(data=val[X],
                    label=val[y],
                    cat_features=cat_features
                    )

    test_data = Pool(data=test[X],
                     label=test[y],
                     cat_features=cat_features
                     )

    model = CatBoostRegressor()

    model.fit(train_data, eval_set=val_data)
    model.predict(test[X])
    test['prediction'] = model.predict(test[X])
    # print(model.get_feature_importance(prettified=True))

    def error(y_true, y_pred):
        print('MAE:', mean_absolute_error(y_true, y_pred))
        print('MAPE:', mean_absolute_percentage_error(y_true, y_pred))
        print('R2:', r2_score(y_true, y_pred))

    # error(test['Burn_Rate'], test['prediction'])

    df_1 = pd.read_csv('docs/' + path)
    df_1 = df_1.rename({'Date of Joining': 'Date_of_Joining',
                        'Company Type': 'Service',
                        'WFH Setup Available': 'remotely',
                        'Resource Allocation': 'Resource_Allocation',
                        'Mental Fatigue Score': 'Mental_Fatigue_Score',
                        'Burn Rate': 'Burn_Rate'
                        }, axis=1)
    df_1 = df_1.drop(columns='Employee ID')

    df_1['Gender'] = df_1['Gender'].replace({'Male': 1, 'Female': 0})
    df_1['Service'] = df_1['Service'].replace({'Service': 1, 'Product': 0})
    df_1['remotely'] = df_1['remotely'].replace({'Yes': 1, 'No': 0})

    test_d = Pool(data=df_1, cat_features=cat_features)
    a = model.predict(df_1)

    df_1['Burn Rate'] = a
    df_1 = df_1.loc[(df_1['Burn Rate'] > 0.75)]
    print(path)
    df_1.to_csv('results/' + path)


def check_csv(path):
    filename, file_extension = os.path.splitext(path)
    ll = ['Employee ID', 'Date of Joining', 'Gender', 'Company Type', 'WFH Setup Available', 'Designation',
          'Resource Allocation', 'Mental Fatigue Score']
    if file_extension == '.csv':
        df = pd.read_csv(path, encoding='unicode_escape')
        for i in df.columns:
            if i in ll:
                pass
            else:
                return 'Ваши данные не подходят под наши параметры!'
        return 'Данные подходят под наши параметры!'
    else:
        return 'Ваши данные не подходят под наши параметры!'


def check_count(path):
    df = pd.read_csv(path + '.csv')
    return df.shape[0]
