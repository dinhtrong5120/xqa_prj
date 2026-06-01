import numpy as np
import pandas as pd
import warnings
import time

warnings.filterwarnings("ignore")


def create_list_columns(df_filter):
    result_list = df_filter.apply(lambda col: col.name if not all(
        pd.isna(x) or x == "YES" for x in col) or "YES" not in col.values else None).dropna().tolist()
    return result_list


def combine_dataframe(df, columns_to_compare, KCA_Project_group_columns_f, Comment_columns_f):
    i = 6
    num_rows = df.shape[0]
    num_columns = df.shape[1]
    df[f'{num_columns}'] = np.nan
    while i < num_rows - 1:
        if df.loc[i, f'{num_columns}'] == 1:
            i += 1
            continue
        temp = i
        j = i + 1
        check_flag = True
        while j < num_rows and check_flag:
            if df.loc[j, f'{num_columns}'] == 1:
                j += 1
                continue
            else:
                None
            a = str(df.iloc[i, 1])[:16]
            b = str(df.iloc[j, 1])[:16]
            if a == b:
                KCA_Project_group_string_i = concat_string(df, i, KCA_Project_group_columns_f)
                KCA_Project_group_string_j = concat_string(df, j, KCA_Project_group_columns_f)
                Comment_string_i = concat_string(df, i, Comment_columns_f)
                Comment_string_j = concat_string(df, j, Comment_columns_f)
                if df.loc[i, columns_to_compare].equals(
                        df.loc[j, columns_to_compare]) and KCA_Project_group_string_i.find(
                    KCA_Project_group_string_j) != -1 and Comment_string_i.find(Comment_string_j) != -1:
                    columns_with_nan_i = df.columns[df.loc[i].isna()].tolist()
                    columns_with_nan_j = df.columns[df.loc[j].isna()].tolist()
                    colol = list(set(columns_with_nan_i) - set(columns_with_nan_j))
                    df.loc[i, colol] = df.loc[j, colol]
                    df.loc[j, f'{num_columns}'] = 1
                    df.iloc[j, 1] = df.iloc[i, 1]
                    check_flag = True
                else:
                    check_flag = True
                    if len(df.iloc[i, 1]) > 16:
                        # df.iloc[j, 1] = a + f"-d000{int(df.iloc[i, 1][-1]) + 1}"
                        next_num = get_next_index(df.iloc[i, 1])
                        df.iloc[j, 1] = a + f"-d{next_num:04d}"
                    elif len(df.iloc[i, 1]) == 16 and j - i == 1:
                        df.iloc[j, 1] = a + f"-d0001"
                    elif len(df.iloc[i, 1]) == 16 and j - i > 1:
                        # df.iloc[j, 1] = a + f"-d000{int(df.iloc[temp, 1][-1]) + 1}"
                        next_num = get_next_index(df.iloc[temp, 1])
                        df.iloc[j, 1] = a + f"-d{next_num:04d}"
                        temp = j
                    else:
                        None
                    j += 1

            else:
                check_flag = False
        i += 1
    df = df[df[f'{num_columns}'] != 1]
    return df


"""The main function running the program."""


def merge_row_cadics(df):
    df_filter = df.iloc[6:, :]

    columns_to_compare = create_list_columns(df_filter)

    KCA_Project_group_columns = df.columns[df.isin(['KCA Project group']).any()].tolist()
    Comment_columns = df.columns[df.isin(['Comment']).any()].tolist()
    ignore_columns = KCA_Project_group_columns + Comment_columns + [1]
    for index in ignore_columns:
        try:
            columns_to_compare.remove(index)
        except:
            None
    end_df = combine_dataframe(df, columns_to_compare, KCA_Project_group_columns, Comment_columns)
    return end_df


def concat_string(df, index, list_concat_string):
    string = "_"
    for sub_index in list_concat_string:
        value = df.iloc[index, sub_index]
        if isinstance(value, str):
            string = string + value
    return string

import re

def get_next_index(val):
    m = re.search(r'-d(\d+)$', str(val))
    if m:
        return int(m.group(1)) + 1
    return 1

