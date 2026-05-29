import pandas as pd
import ast
import streamlit
from xqa_web.app.setting import BASE_DIR_HISTORY_FILE

def region_1(result_querry_region1):
    data = []
    list_sap_xep_0 = ["CCM", "ZONE", "BODY", "ENGINE", "AXLE", "HANDLE", "GRADE", "TRANS", "YEAR", "INTAKE", "SEAT",
                      "NUMBER"]
    for project in result_querry_region1:
        data.append({
            'auto': project.auto_infor,
            'gr': project.group_infor,
            'keyword': project.keyword,
            'CADICS ID': project.parameter_name
        })

    df_1 = pd.DataFrame(data)
    df_1 = df_1.replace('null', None)
    df_1['device_name_order'] = df_1['CADICS ID'].apply(
        lambda x: list_sap_xep_0.index(x) if x in list_sap_xep_0 else len(list_sap_xep_0))
    df_1 = df_1.sort_values(by=['device_name_order'])
    df_1 = df_1.drop(columns=['device_name_order'])
    return df_1


def region_2(result_querry_region2):
    df_2_begin = pd.DataFrame(result_querry_region2,
                              columns=['CADICS ID', 'Project', 'Config', 'Value'])
    df_2 = df_2_begin.pivot(index='CADICS ID', columns='Config', values='Value')
    df_2.reset_index(inplace=True)
    return df_2


def region_3(result_querry_region3):
    df_3_begin = pd.DataFrame(result_querry_region3,
                              columns=['CADICS ID', 'keyword', 'gr', 'auto', 'Project', 'Config', 'Value'])

    df_3 = df_3_begin.pivot(index='CADICS ID', columns='Config', values='Value')
    df_3.reset_index(inplace=True)
    return df_3


def region_4(results_querry_region_4, index_df_1):
    df_4_begin = pd.DataFrame(results_querry_region_4,
                              columns=['device_group', 'device_name', 'auto', 'group_detail', 'option_detail',
                                       'device_details_name', 'group_key_map', 'default'])
    with open(BASE_DIR_HISTORY_FILE, 'r') as file:
        data = file.read()

    # Chuyển đổi chuỗi thành danh sách
    list_sap_xep = ast.literal_eval(data)
    # Tạo cột ánh xạ thứ tự cho `device_name`
    df_4_begin['device_name_order'] = df_4_begin['device_name'].apply(
        lambda x: list_sap_xep.index(x) if x in list_sap_xep else len(list_sap_xep))
    df_4_sorted = df_4_begin.sort_values(by=['device_group', 'device_name_order'])
    df_4_sorted = df_4_sorted.drop(columns=['device_name_order'])
    column_max_list = df_4_sorted.iloc[:, 0].tolist()
    unique_list_max = list(set(column_max_list))

    column_submax_list = df_4_sorted.iloc[:, 1].tolist()
    unique_list_submax = list(set(column_submax_list))
    result_tuple = [tuple(row) for row in df_4_sorted.to_records(index=False)]
    col_auto = []
    col_gr = []
    col_keyword = []
    col_CADICS_ID = []
    col_group_key_map = []
    col_default = []
    col_device_name = []
    for row in result_tuple:
        col_auto.extend([row[0], row[1], row[2]])
        col_gr.extend(['', '', row[3]])
        col_keyword.extend(['', '', row[4]])
        col_CADICS_ID.extend(['', '', row[5]])
        col_group_key_map.extend(['', '', row[6]])
        col_default.extend(['', '', row[7]])
        col_device_name.extend(['', '', row[1]])
    df_4 = pd.DataFrame({
        'auto': col_auto,
        'gr': col_gr,
        'keyword': col_keyword,
        'CADICS ID': col_CADICS_ID,
        'group_key_map': col_group_key_map,
        'default': col_default,
        'device_name': col_device_name
    })
    df_null_rows = df_4[(df_4['auto'] == '') | (df_4['CADICS ID'] != '')]
    df_non_null_rows = df_4[(df_4['auto'] != '') & (df_4['CADICS ID'] == '')]
    df_non_null_deduplicated = df_non_null_rows.drop_duplicates(subset=['auto'], keep='first')
    df_4 = pd.concat([df_null_rows, df_non_null_deduplicated])

    df_4 = df_4.sort_index()
    df_4 = df_4.replace('null', None)
    df_4 = df_4[
        (df_4['auto'] != 'UNKNOW_device_group') & (df_4['auto'] != 'UNKNOW_device')]
    df_4 = df_4.reset_index(drop=True)
    df_4.index = df_4.index + index_df_1 + 1
    return df_4, unique_list_max, unique_list_submax


def region_6(result_querry_region6):
    df_6_begin = pd.DataFrame(result_querry_region6,
                              columns=['Project', 'CADICS ID', 'device_name', 'gr', 'Comment_column', 'Value'])
    df_6_version2 = df_6_begin[['CADICS ID', 'device_name', 'gr', 'Comment_column', 'Value']]
    df_6 = df_6_version2.pivot(index=['CADICS ID', 'device_name', 'gr'], columns='Comment_column', values='Value')
    df_6.reset_index(inplace=True)
    return df_6


def region_7(results_querry_region_7, index_df_4):
    df_7_pull_sql = pd.DataFrame(results_querry_region_7, columns=['Project', 'Config', 'Lot', 'OptionCode', 'value'])
    df_7_pull_sql.replace('', None, inplace=True)
    df_lot_optioncode = df_7_pull_sql.pivot(index='Lot', columns='Config', values='value')
    df_lot_optioncode.reset_index(inplace=True)
    df_lot_optioncode.index = df_lot_optioncode.index + 1
    df_temp_1 = df_7_pull_sql[['Config', 'OptionCode', 'Lot']]
    df_temp_2 = df_temp_1.pivot(index='Lot', columns='Config', values='OptionCode')
    df_temp_2.reset_index(inplace=True)
    df_row_optioncode_name = df_temp_2.iloc[[0]]
    df_row_optioncode_name.at[0, 'Lot'] = 'OptionCode'
    df_7 = pd.concat([df_row_optioncode_name, df_lot_optioncode], axis=0)
    df_7.index = df_7.index + index_df_4 + 1
    df_7.rename(columns={'Lot': 'CADICS ID'}, inplace=True)
    df_7 = df_7.replace('null', None)
    return df_7


def region_8(result_querry_region8):
    df_8_version1 = pd.DataFrame(result_querry_region8,
                                 columns=['Project', 'Config', 'device_name', 'CADICS ID', 'gr', 'Value'])
    df_8_version2 = df_8_version1[['Config', 'gr', 'CADICS ID', 'device_name', 'Value']]
    df_8 = df_8_version2.pivot(index=['gr', 'CADICS ID', 'device_name'], columns='Config', values='Value')
    df_8.reset_index(inplace=True)
    return df_8
