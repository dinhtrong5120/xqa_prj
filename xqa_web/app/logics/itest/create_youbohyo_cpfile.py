import os
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import json as js
from xqa_web.app.logics.itest.format_cp_output import *

from xqa_web.app.setting import BASE_DIR_DATAS, BASE_DIR_OUTPUTS
# def covert_vehInfo_AABB(df_AABB, veh_name). Use to get and covert data vehicle info from AABB to a Dict
def convert_vehInfo_AABB(df_AABB, veh_name):
    dict_AABB = {}
    for cl in df_AABB.columns:
        next_column_data = pd.Series()
        key = ""
        column_data = pd.Series()
        if veh_name in cl:
            col_index = df_AABB.columns.get_loc(cl)
            # get next column data contain buban name
            if col_index + 1 < len(df_AABB.columns):
                column_data = df_AABB.iloc[1:, col_index]
                next_column_data = df_AABB.iloc[:, col_index + 1]
                key = next_column_data.iloc[0]
                try:
                    key = int(float(key))
                    key = str(key)
                except Exception as e:
                    print("convert app err: ", e)
            else:
                print("Cột 'A' là cột cuối cùng, không có cột tiếp theo.")
        column_data = column_data.to_dict()
        if key != "":
            dict_AABB[key]= dict()
            dict_AABB[key]= column_data
    return dict_AABB

# RUNING -----------------------------------------------------------------------------------------------------------------------
def cp_youbo_file(list_option_base, option_taiso, link_match_jikken_trigger, youbohyo_compare_output):
    # INPUT ----------------------------
    link_aabb = os.path.join(BASE_DIR_DATAS, 'AABB表.xlsx')
    link_youbo_taiso = os.path.join(BASE_DIR_OUTPUTS, option_taiso, 'Car配車要望表.xlsx')
    taiso_name = option_taiso.split('_')[0]
    list_name_base = []
    list_link_base = []
    for option_base in list_option_base:
        name_base = option_base.split('_')[0]
        link_base = os.path.join(BASE_DIR_OUTPUTS, option_base, 'Car配車要望表.xlsx')
        list_link_base.append(link_base)
        list_name_base.append(name_base)
        
        
    # RUNING ---------------------------
    df_AABB = pd.read_excel(link_aabb, header=4, sheet_name="Family COCA LIST", engine='calamine')
    dict_taiso_AABB = convert_vehInfo_AABB(df_AABB, taiso_name)
    df_youbo_full_taiso = pd.read_excel(link_youbo_taiso, sheet_name=None, engine='calamine')
    for base_cnt in range(len(list_name_base)):
        base_name = list_name_base[base_cnt]
        dict_base_AABB = convert_vehInfo_AABB(df_AABB, base_name)
        df_youbo_full_base = pd.read_excel(list_link_base[base_cnt], sheet_name=None, engine='calamine')

        with open(link_match_jikken_trigger, 'r', encoding='utf-8') as file:
            dict_jikken_match = js.load(file)
            
        dict_match_AABB = dict()
        dict_match_AABB[taiso_name + '-' + base_name] = dict()
        list_app_taiso = list()
        list_app_base = list()
        for app_taiso in dict_taiso_AABB.keys():
            list_app_taiso.append(app_taiso)
            dict_match_AABB[taiso_name + '-' + base_name] [app_taiso] = list()
            for row_taiso in dict_taiso_AABB[app_taiso].keys():
                if row_taiso == 1 :
                    pass
                else:
                    # Check match in base vehicle 
                    for app_base in dict_base_AABB.keys():
                        try:
                            if dict_taiso_AABB[app_taiso][row_taiso] == dict_base_AABB[app_base][row_taiso]:
                                list_app_base.append(app_base)
                                if not app_base in dict_match_AABB[taiso_name + '-' + base_name] [app_taiso]:
                                    dict_match_AABB[taiso_name + '-' + base_name] [app_taiso].append(app_base) 
                                else:
                                    pass
                            else:
                                pass
                        except:
                            pass
        list_app_base = list(set(list_app_base))
        # Create cp file 
        output_file = youbohyo_compare_output
        if os.path.exists(output_file):
            os.remove(output_file)
        else:
            pass
        empty_df = pd.DataFrame()
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            empty_df.to_excel(writer, index=False, sheet_name='Sheet1')
            
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name in df_youbo_full_taiso:
                # Check Do base have sheet of taiso :
                if sheet_name in df_youbo_full_base:
                    # convert data of df and dict_app_AABB
                    df_youbo_full_taiso[sheet_name].loc[3] = df_youbo_full_taiso[sheet_name].loc[3].fillna('').apply(lambda x: int(x) if isinstance(x, float) else x)
                    df_youbo_full_taiso[sheet_name].loc[3] = df_youbo_full_taiso[sheet_name].iloc[3].fillna('').apply(lambda x: str(x) if isinstance(x, int) else x)
                    df_youbo_full_base[sheet_name].loc[3] = df_youbo_full_base[sheet_name].loc[3].fillna('').apply(lambda x: int(x) if isinstance(x, float) else x)
                    df_youbo_full_base[sheet_name].loc[3] = df_youbo_full_base[sheet_name].loc[3].fillna('').apply(lambda x: str(x) if isinstance(x, int) else x)
                    # cl_group = 1
                    # cl_sub_info = [2,3,4,5]
                    # cl_file_name = 152
                    # cl_jikken = 161
                    list_cl_use = [0,1,2,3,4,151,160]
                    dict_cl_app_taiso = dict()
                    for app_taiso in list_app_taiso:
                        cl_app_taiso = df_youbo_full_taiso[sheet_name].columns[df_youbo_full_taiso[sheet_name].iloc[3] == app_taiso]
                        # handle for dont find app in youbouhyo
                        try:
                            dict_cl_app_taiso[app_taiso] = int(cl_app_taiso[0].split(': ')[1])
                        except:
                            dict_cl_app_taiso[app_taiso] = 0
                    dict_cl_app_taiso = dict(sorted(dict_cl_app_taiso.items(), key=lambda item: item[1]))
                    list_cl_app_taiso_use = sorted(list(dict_cl_app_taiso.values()) + list_cl_use)
                    df_taiso_use = df_youbo_full_taiso[sheet_name].iloc[:, list_cl_app_taiso_use]
                    df_taiso_use = df_taiso_use.fillna('')
                    for app_taiso in dict_cl_app_taiso.keys():
                        column_to_modify = dict_cl_app_taiso[app_taiso]
                        df_taiso_use.iloc[:, column_to_modify] = df_taiso_use.iloc[:, column_to_modify].replace('*', '')
                        df_taiso_use.iloc[:, column_to_modify] = df_taiso_use.iloc[:, column_to_modify].where(df_taiso_use.iloc[:, column_to_modify]=='',app_taiso)
                    for app_taiso in dict_cl_app_taiso.keys():
                        try:
                            df_taiso_use['app_find'] = df_taiso_use.iloc[:,dict_cl_app_taiso[app_taiso]] + df_taiso_use['app_find']
                        except:
                            df_taiso_use['app_find'] = df_taiso_use.iloc[:,dict_cl_app_taiso[app_taiso]]
                    
                    
                    dict_cl_app_base = dict()   
                    for app_base in list_app_base:
                        cl_app_base = df_youbo_full_base[sheet_name].columns[df_youbo_full_base[sheet_name].iloc[3] == app_base]
                        # handle for dont find app in youbouhyo
                        try:
                            dict_cl_app_base[app_base] = int(cl_app_base[0].split(': ')[1])
                        except:
                            dict_cl_app_base[app_base] = 0
                    dict_cl_app_base = dict(sorted(dict_cl_app_base.items(), key=lambda item: item[1]))
                    list_cl_app_base_use = sorted(list(dict_cl_app_base.values()) + list_cl_use)
                    df_base_use = df_youbo_full_base[sheet_name].iloc[:, list_cl_app_base_use]
                    df_base_use = df_base_use.fillna('')
                    for app_base in dict_cl_app_base.keys():
                        column_to_modify = dict_cl_app_base[app_base]
                        df_base_use.iloc[:, column_to_modify] = df_base_use.iloc[:, column_to_modify].replace('*', '')
                        df_base_use.iloc[:, column_to_modify] = df_base_use.iloc[:, column_to_modify].where(df_base_use.iloc[:, column_to_modify]=='',app_base)
                    for app_base in dict_cl_app_base.keys():
                        try:
                            df_base_use['app_find'] = df_base_use.iloc[:,dict_cl_app_base[app_base]] + df_base_use['app_find']
                        except:
                            df_base_use['app_find'] = df_base_use.iloc[:,dict_cl_app_base[app_base]]
                    
                    
                    # Find row match to create compare Dataframe
                    # 8,9 is column of df after handle 
                    list_result_cl_name = ['ファイル名', '実験識別', '実験種別', '実験項目', '変更後実験実施時期']
                    list_result_cl_name.extend(list_app_taiso) 
                    list_result_cl_name.extend(['*実験計画者', '実験']) 
                    
                    list_result_base_cl_name = ['ファイル名', '実験識別', '実験種別', '実験項目', '変更後実験実施時期']
                    list_result_base_cl_name.extend(list_app_base) 
                    list_result_base_cl_name.extend(['*実験計画者', '実験']) 
                    
                    df_base_after_cp = pd.DataFrame(columns=list_result_base_cl_name)
                    df_taiso_after_cp = pd.DataFrame(columns=list_result_cl_name)
                    df_result_cp = pd.DataFrame(columns=list_result_cl_name)
                    index_match_base = list()
                    # cnt_row_taiso = cnt_row_base = cnt_row_resul = 6
                    
                    for index_taiso, row_taiso in df_taiso_use.iterrows():                    
                        if index_taiso > (17):
                            # Check match_unmatch
                            flg_match_jikken = False
                            key_find = str(row_taiso[0]).upper() + '_VC実験削減 要件表.xlsx'
                            if key_find in dict_jikken_match:
                                if row_taiso[6+len(list_app_taiso)] in dict_jikken_match[key_find]:
                                    flg_match_jikken = True
                                    
                            if flg_match_jikken:       
                                flg_match = False
                                if row_taiso[7+len(list_app_taiso)] in dict_match_AABB[taiso_name + '-' + base_name]:
                                    index_find_base = df_base_use[(df_base_use.iloc[:, 5+len(list_app_base)] == row_taiso[5+len(list_app_taiso)]) & (df_base_use.iloc[:, 6+len(list_app_base)] == row_taiso[6+len(list_app_taiso)])].index
                                    index_find_base.tolist()
                                    flg_write_taiso_status = False
                                    for index_base in index_find_base:
                                        app_base_in_row = df_base_use.iloc[index_base, 7+len(list_app_base)]
                                        # Case 1 : Taiso and base match
                                        if (app_base_in_row in dict_match_AABB[taiso_name + '-' + base_name][row_taiso[7+len(list_app_taiso)]]): 
                                            flg_match = True
                                            # for taiso 
                                            if flg_write_taiso_status == False:
                                                new_row_taiso_after_cp = pd.Series()
                                                for new_cl, old_cl in zip(list_result_cl_name, list_cl_app_taiso_use):
                                                    new_row_taiso_after_cp[new_cl] = df_youbo_full_taiso[sheet_name].iloc[index_taiso,old_cl]                         
                                                df_taiso_after_cp = pd.concat([df_taiso_after_cp, new_row_taiso_after_cp.to_frame().T], ignore_index=True)
                                            else:
                                                new_row_taiso_after_cp = pd.Series()
                                                for new_cl in list_result_cl_name:
                                                    new_row_taiso_after_cp[new_cl] = "blue"                        
                                                df_taiso_after_cp = pd.concat([df_taiso_after_cp, new_row_taiso_after_cp.to_frame().T], ignore_index=True)
                                            # for result
                                            new_row_result_after_cp = pd.Series()
                                            for new_cl in list_result_base_cl_name:
                                                new_row_result_after_cp[new_cl] = "yellow"                         
                                            df_result_cp = pd.concat([df_result_cp, new_row_result_after_cp.to_frame().T], ignore_index=True)
                                            # for base    
                                            if not index_base in index_match_base:
                                                index_match_base.append(index_base)       
                                                new_row_base_after_cp = pd.Series()
                                                for new_cl, old_cl in zip(list_result_base_cl_name, list_cl_app_base_use):
                                                    new_row_base_after_cp[new_cl] = df_youbo_full_base[sheet_name].iloc[index_base,old_cl]                            
                                                df_base_after_cp = pd.concat([df_base_after_cp, new_row_base_after_cp.to_frame().T], ignore_index=True)
                                            else:
                                                new_row_base_after_cp = pd.Series()
                                                for new_cl in list_result_base_cl_name:
                                                    new_row_base_after_cp[new_cl] = "blue"                          
                                                df_base_after_cp = pd.concat([df_base_after_cp, new_row_base_after_cp.to_frame().T], ignore_index=True)
                                            flg_write_taiso_status = True
                                                
                                    # Case 2 : Taiso have . base haven't
                                    if flg_match == False:
                                        # for taiso 
                                        new_row_taiso_after_cp = pd.Series()
                                        for new_cl, old_cl in zip(list_result_cl_name, list_cl_app_taiso_use):
                                            new_row_taiso_after_cp[new_cl] = df_youbo_full_taiso[sheet_name].iloc[index_taiso,old_cl]
                                        df_taiso_after_cp = pd.concat([df_taiso_after_cp, new_row_taiso_after_cp.to_frame().T], ignore_index=True)
                                        # for base                             
                                        new_row_base_after_cp = pd.Series()
                                        for new_cl in list_result_base_cl_name:
                                            new_row_base_after_cp[new_cl] = "yellow"                           
                                        df_base_after_cp = pd.concat([df_base_after_cp, new_row_base_after_cp.to_frame().T], ignore_index=True)
                                        # for result
                                        new_row_result_after_cp = pd.Series()
                                        for new_cl, old_cl in zip(list_result_cl_name, list_cl_app_taiso_use):
                                            new_row_result_after_cp[new_cl] = df_youbo_full_taiso[sheet_name].iloc[index_taiso,old_cl]                            
                                        df_result_cp = pd.concat([df_result_cp, new_row_result_after_cp.to_frame().T], ignore_index=True)
                            else:
                                pass
                                                      
                    # df preprocessing
                    def df_pre_process(df, str_head, list_app):
                        str_head = str(str_head)
                        df_copy = df.copy()
                        df_copy[list_app] = df_copy[list_app].apply(pd.to_numeric, errors='coerce')
                        total_sum = df_copy[list_app].sum().sum()
                        list_header = df.columns.tolist()
                        dict_data = dict()
                        for header in list_header:
                            dict_data[header] = list()
                            if header == 'ファイル名': 
                                dict_data[header].append(str_head)
                            elif header == '実験':
                                dict_data[header].append(total_sum)
                            else:
                                dict_data[header].append('')
                        df = pd.concat([pd.DataFrame(dict_data), df], ignore_index= True)
                        return df
                    
                    df_base_after_cp = df_pre_process(df_base_after_cp, '１番手', list_app_base)
                    df_taiso_after_cp= df_pre_process(df_taiso_after_cp, '２番手削除前', list_app_taiso)
                    df_result_cp = df_pre_process(df_result_cp, '２番手削除後', list_app_taiso)
                    
                    # Create output cp file 
                    num_rows = max(len(df_base_after_cp), len(df_taiso_after_cp), len(df_result_cp))
                    df_large = pd.DataFrame(index=range(num_rows))
                    df_large = pd.concat([df_large, df_base_after_cp], axis=1)
                    df_large = pd.concat([df_large, pd.DataFrame(columns=['', ''])], axis=1) 
                    df_large = pd.concat([df_large, df_taiso_after_cp], axis=1)
                    df_large = pd.concat([df_large, pd.DataFrame(columns=['', ''])], axis=1) 
                    df_large = pd.concat([df_large, df_result_cp], axis=1)
                    
                    # Swap header and row1
                    header_row = pd.DataFrame([df_large.columns.tolist()], columns=df_large.columns)
                    df_with_header_copy = pd.concat([header_row, df_large], ignore_index=True)
                    df_with_header_copy.iloc[[0,1]] = df_with_header_copy.iloc[[1,0]].values
                    df_with_header_copy.columns = df_with_header_copy.iloc[0]
                    df_with_header_copy = df_with_header_copy[1:]
                    df_with_header_copy.reset_index(drop=True, inplace=True)
                    
                    # Write to excel 
                    df_with_header_copy.to_excel(writer, index=False, sheet_name=sheet_name)
                    
                    # Create output Compare
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]
                    
                    # setup color
                    fill_yellow = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')  # color : yellow
                    fill_blue = PatternFill(start_color='2EF1F6', end_color='2EF1F6', fill_type='solid')  # color: blue
                    fill_green = PatternFill(start_color='00B050', end_color='00B050', fill_type='solid')  # color: green
                    
                    # Save list row need to delete
                    rows_to_delete = []
                    for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=0, max_col=worksheet.max_column):
                        flg_blank_row = False
                        for cell in row:
                            if str(cell.value).strip() == 'blue':
                                cell.fill = fill_blue
                                cell.value = ''
                            elif str(cell.value).strip() == 'yellow':
                                cell.fill = fill_yellow
                                cell.value = ''
                            elif str(cell.value).strip() == 'green':
                                cell.fill = fill_green
                                cell.value = ''
                            else:
                                pass
                            if str(cell.value).strip() != '':
                                flg_blank_row = True
                        if not flg_blank_row:
                            rows_to_delete.append(row[0].row)
                    # Delete row 
                    for row_index in reversed(rows_to_delete):
                        worksheet.delete_rows(row_index)
            else:
                pass
    process_compare_output(output_file)
            