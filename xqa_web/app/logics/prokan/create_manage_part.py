import pandas as pd
import unicodedata

import time


def normalize_japanese_text(input_text):
    normalized_text = ''
    if isinstance(input_text, str):
        for char in input_text:
            normalized_char = unicodedata.normalize('NFKC', char)
            normalized_text += normalized_char
        normalized_text = normalized_text.replace("\n", "")
        normalized_text = normalized_text.strip()
        return normalized_text
    else:
        return input_text


def create_manage_part(df_karen4_, df_cadics_, lot):
    dic_address = {"DS": [54, 58, 59, 66], "DC": [54, 58, 59, 73], "PFC": [74, 78, 79, 90], "VC": [91, 95, 96, 106],
                   "PT1": [91, 95, 96, 116], "PT2": [91, 95, 96, 126]}
    list_col_copy_data = []
    if df_cadics_.shape[0]<7:
        return []
    
    try:
        col_df2 = df_karen4_.columns[df_karen4_.isin(['特性管理部品']).any()].values[0]
    except:
        col_df2=len(df_karen4_.columns)
    df_table_2 = df_karen4_.iloc[16:, col_df2:]
    if df_karen4_.shape[0] < 20:
        return []
    dict_col_maru = {column: df_karen4_.loc[df_karen4_[column].isin(['〇', '○']), 0].tolist()
                     for column in df_table_2.columns if df_table_2[column].isin(['〇', '○']).any()}
    if not dict_col_maru or pd.isna(df_karen4_.iloc[19, 0]):
        return []
    index_first_containing_cadics_code = None
    col1_list_cadics = df_cadics_.iloc[:, 1].tolist()
    for key, value in dict_col_maru.items():
        for item in value:
            lower_item = item.lower()
            rows_found_cadics = next(
                (i for i, value in enumerate(col1_list_cadics) if lower_item in str(value).lower()), None)
            if rows_found_cadics:
                index_first_containing_cadics_code = rows_found_cadics
                break
            else:
                pass

        if index_first_containing_cadics_code is not None:
            list_col_copy_data.append(key)
            df_karen4_.iloc[1, key] = df_cadics_.iloc[6, dic_address.get(lot)[1]]
            df_karen4_.iloc[3, key] = df_cadics_.iloc[6, dic_address.get(lot)[2]]
    end_list_dict = [dict((i, df_karen4_.loc[i, key]) for i in range(16)) for key in
                     list_col_copy_data] if list_col_copy_data else []

    return end_list_dict

