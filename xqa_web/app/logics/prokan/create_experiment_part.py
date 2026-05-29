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


def create_experiment_part(df_karen4_, df_cadics_, df_syo_,lot):
    dic_address = {"DS": [54, 58, 59, 66], "DC": [54, 58, 59, 73], "PFC": [74, 78, 79, 90], "VC": [91, 95, 96, 106],
                   "PT1": [91, 95, 96, 116], "PT2": [91, 95, 96, 126]}
    time_1_2 = 0
    list_col_copy_data = []
    try:
        col_df2 = df_karen4_.columns[df_karen4_.isin(['特性管理部品']).any()].values[0]
    except:
        col_df2=len(df_karen4_.columns)
    df_table_1 = df_karen4_.iloc[:, 0:(col_df2 - 1)]
    if df_karen4_.shape[0] < 20:
        return []
    dict_col_maru = {column: df_table_1.loc[df_table_1[column].isin(['〇', '○']), 0].tolist()
                     for column in df_table_1.columns if df_table_1[column].isin(['〇', '○']).any()}
    if not dict_col_maru or pd.isna(df_karen4_.iloc[19, 0]):
        return []
    index_first_containing_cadics_code = None
    col1_list_cadics = df_cadics_.iloc[:, 1].tolist()
    for key, value in dict_col_maru.items():
        for item in value:
            time_1 = time.time()
            lower_item = item.lower()
            rows_found_cadics = next(
                (i for i, value in enumerate(col1_list_cadics) if lower_item in str(value).lower()), None)
            time_2 = time.time()
            time_1_2 += (time_2 - time_1)
            if rows_found_cadics:
                index_first_containing_cadics_code = rows_found_cadics
                break
            else:
                pass

        if index_first_containing_cadics_code is not None:
            list_col_copy_data.append(key)
            df_karen4_.iloc[3, key] = df_karen4_.iloc[8, key] = df_cadics_.iloc[6, dic_address.get(lot)[1]]
            df_karen4_.iloc[2, key] = df_cadics_.iloc[6, dic_address.get(lot)[2]]
    if not list_col_copy_data:
        return []
    end_list_dict = [dict((i, df_karen4_.loc[i, key]) for i in range(16)) for key in
                     list_col_copy_data] if list_col_copy_data else []

    end_list_dict_dup = []

    for dict_sub in end_list_dict:
        option = dict_sub.get(15)
        if option and not pd.isna(option):
            dict_equipment = {}
            rows_found_option = df_syo_.index[df_syo_[3].str.lower() == option.lower()]
            if not rows_found_option.empty:
                list_item_of_value = [df_syo_.iloc[rows_found_option[0], 5 + i] for i in range(5)]
                dict_equipment[option] = list(set(list_item_of_value))
            else:
                dict_equipment[option] = []
            for value in dict_equipment.values():
                for item_value in value:
                    dict_sub_ref = dict_sub.copy()
                    dict_sub_ref[12] = f"{dict_sub[12]}, {item_value}"
                    dict_sub_ref[21]=dict_sub_ref[15]
                    del dict_sub_ref[15]
                    end_list_dict_dup.append(dict_sub_ref)
        else:
            dict_sub[21]=dict_sub[15]
            del dict_sub[15]
            end_list_dict_dup.append(dict_sub)

    return end_list_dict_dup

