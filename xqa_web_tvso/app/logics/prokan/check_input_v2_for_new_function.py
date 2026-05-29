import os
import openpyxl
import pandas as pd
import numpy as np
from openpyxl.styles import Font
from openpyxl.styles import PatternFill


def create_list_all_file_name_replaced(list_files):
    list_file_name_replaced = []
    for file in list_files:
        end_location_replace = file.rfind(')')
        replace_file_name = file[4:end_location_replace + 1].replace('_', '').replace(' ', '')
        list_file_name_replaced.append(replace_file_name)
    return list_file_name_replaced


def write_list_file_name_into_df(df_status_all_karen_file, final_list_name_file, replace_name_karen,
                                 list_file_name_karen_after_replaced,
                                 column_name):
    for index_in_list_final, value_in_list_final in enumerate(final_list_name_file):
        flg_check_found = False
        index_file_name_in_list = None
        for ele_index, element in enumerate(replace_name_karen):
            if element == value_in_list_final:
                index_file_name_in_list = ele_index
                flg_check_found = True
                break
        if flg_check_found:
            df_status_all_karen_file.loc[index_in_list_final, column_name] = list_file_name_karen_after_replaced[
                index_file_name_in_list]
        else:
            df_status_all_karen_file.loc[index_in_list_final, column_name] = np.nan
            # df.loc[index_in_list_final, 'Comment'] = "Error"
    return df_status_all_karen_file


def create_status_all_karen_file(karen1_files, karen2_files, karen3_files, karen4_files):
    list_all_file_from_4_karen = []
    list_all_file_from_4_karen.extend(karen1_files)
    list_all_file_from_4_karen.extend(karen2_files)
    list_all_file_from_4_karen.extend(karen3_files)
    list_all_file_from_4_karen.extend(karen4_files)
    list_all_file_after_replaced_file_name = create_list_all_file_name_replaced(list_all_file_from_4_karen)
    list_all_file_after_replaced_file_name.sort()

    list_all_file_name = []
    for name_file in list_all_file_after_replaced_file_name:
        if len(list_all_file_name) == 0:
            list_all_file_name.append(name_file)
            continue
        if name_file not in list_all_file_name:
            list_all_file_name.append(name_file)

    list_file_name_karen1_after_replaced = create_list_all_file_name_replaced(karen1_files)
    list_file_name_karen2_after_replaced = create_list_all_file_name_replaced(karen2_files)
    list_file_name_karen3_after_replaced = create_list_all_file_name_replaced(karen3_files)
    list_file_name_karen4_after_replaced = create_list_all_file_name_replaced(karen4_files)
    # df_status_all_karen_file = pd.DataFrame(columns=['関連表①', '関連表②', '関連表③', '関連表④', 'Comment'])
    df_status_all_karen_file = pd.DataFrame(columns=['関連表①', '関連表②', '関連表③', '関連表④'])

    df_status_all_karen_file = write_list_file_name_into_df(df_status_all_karen_file, list_all_file_name,
                                                            list_file_name_karen1_after_replaced, karen1_files,
                                                            '関連表①')
    df_status_all_karen_file = write_list_file_name_into_df(df_status_all_karen_file, list_all_file_name,
                                                            list_file_name_karen2_after_replaced, karen2_files,
                                                            '関連表②')
    df_status_all_karen_file = write_list_file_name_into_df(df_status_all_karen_file, list_all_file_name,
                                                            list_file_name_karen3_after_replaced, karen3_files,
                                                            '関連表③')
    df_status_all_karen_file = write_list_file_name_into_df(df_status_all_karen_file, list_all_file_name,
                                                            list_file_name_karen4_after_replaced, karen4_files,
                                                            '関連表④')
    return df_status_all_karen_file
